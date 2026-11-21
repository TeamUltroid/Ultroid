//! How a command is recognised: `compile_pattern` of `pyUltroid/_misc/_decorators.py`, and what
//! Python's `re` module then does with the pattern on a message. Proven in `rust/command-rs`.
//!
//! A plugin registers a regular expression for its command (`ping$`, `ban( (.*)|$)`). Ultroid
//! puts the handler prefix in front and matches it against the start of every message with
//! `re.match`. Which messages are commands, and what `event.pattern_match.group(1)` holds, is
//! decided there.
//!
//! The patterns are written for Python's `re`, and `re` has rules of its own: `$` also matches
//! before a final line break, `\w`, `\d` and `\s` are the characters Python (Unicode 14) counts,
//! `\b` and `\B` both fail in an empty text, and a loop stops once a round has taken nothing. A
//! general regular expression engine answers differently in each of these places, so the
//! pattern is read and matched here the way `re` does it, step for step.
//!
//! What is read: characters and escapes, `.`, classes, `^ $ \A \Z \b \B`, groups (plain,
//! `(?:...)` and `(?P<name>...)`), `|`, the repeats `* + ? {m,n}` and their lazy forms, and
//! references to a group by number. A pattern that uses more of `re` (flags, look-around,
//! conditions, atomic groups) is refused as [`PatternError::Unsupported`], never guessed at.

use crate::tables::{DIGIT, SPACE, WORD};
use std::cmp::Ordering;
use std::fmt;

/// `compile_pattern(data, hndlr)`: the `re` pattern for a command under a handler.
///
/// One leading `^` and then one leading `.` are dropped from the plugin's pattern. With the
/// handler `" "` or `"NO_HNDLR"` the command stands at the start of the message. Otherwise the
/// pattern is a backslash, the handler and the plugin's pattern, so the backslash escapes the
/// first character of the handler, whatever it is.
pub fn command_pattern(data: &str, handler: &str) -> String {
    let data = data.strip_prefix('^').unwrap_or(data);
    let data = data.strip_prefix('.').unwrap_or(data);
    if handler == " " || handler == "NO_HNDLR" {
        format!("^{data}")
    } else {
        format!("\\{handler}{data}")
    }
}

/// The pattern `asst_cmd` compiles for a command of the assistant bot.
pub fn assistant_pattern(pattern: &str) -> String {
    format!("^/{pattern}")
}

/// Why a pattern cannot be used.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum PatternError {
    /// Python's `re.compile` refuses the pattern (`re.error`).
    Bad(&'static str),
    /// The pattern uses a part of `re` this port does not read. Nothing is claimed about it:
    /// Python may accept it or not.
    Unsupported(&'static str),
}

impl fmt::Display for PatternError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Bad(why) => write!(f, "bad pattern: {why}"),
            Self::Unsupported(what) => write!(f, "pattern not supported: {what}"),
        }
    }
}

impl std::error::Error for PatternError {}

/// A count `re` takes in a repeat such as `{2,3}` is below this; from here on Python raises an
/// `OverflowError`.
const TOO_MANY: u32 = u32::MAX;

/// How deep groups may be nested here. `re` reads a few hundred levels before Python's own
/// recursion limit stops it.
const DEEPEST: usize = 100;

/// How many rounds a loop may have to go through without taking a character. `(a?){5}` on a
/// text with no `a` goes five such rounds; with a count in the millions, and loops inside
/// loops, that is work and memory without end, in `re` as much as here.
const IDLEST: u64 = 100_000;

/// Whether a sorted table of inclusive ranges has the character.
fn listed(table: &[(u32, u32)], c: char) -> bool {
    let code = u32::from(c);
    let side = |&(first, last): &(u32, u32)| {
        if last < code {
            Ordering::Less
        } else if first > code {
            Ordering::Greater
        } else {
            Ordering::Equal
        }
    };
    table.binary_search_by(side).is_ok()
}

/// `\d`, `\w` and `\s`: the characters Python counts as a decimal digit, as a letter, a digit of
/// any kind or the underscore, and as white space.
#[derive(Clone, Copy, Debug)]
enum Kind {
    Digit,
    Word,
    Space,
}

impl Kind {
    fn has(self, c: char) -> bool {
        match self {
            Self::Digit => listed(&DIGIT, c),
            Self::Word => listed(&WORD, c),
            Self::Space => listed(&SPACE, c),
        }
    }
}

/// One member of a class.
#[derive(Clone, Debug)]
enum Member {
    One(char),
    Range(char, char),
    /// `\d`, `\w` or `\s`, or with `false` their opposites `\D`, `\W` and `\S`.
    Kind(Kind, bool),
}

/// `[...]` and `[^...]`, and `\d` and the like on their own.
#[derive(Clone, Debug)]
struct Class {
    negated: bool,
    members: Vec<Member>,
}

impl Class {
    fn has(&self, c: char) -> bool {
        let member = |member: &Member| match *member {
            Member::One(one) => one == c,
            Member::Range(first, last) => first <= c && c <= last,
            Member::Kind(kind, inside) => kind.has(c) == inside,
        };
        self.members.iter().any(member) != self.negated
    }
}

/// A place in the text a pattern can ask for.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Place {
    /// `^` and `\A`: the start.
    Start,
    /// `$`: the end, or just before a line break that ends the text.
    End,
    /// `\Z`: the very end.
    VeryEnd,
    /// `\b`: a word character on exactly one side.
    Boundary,
    /// `\B`: a word character on both sides or on neither.
    NotBoundary,
}

impl Place {
    fn holds(self, text: &[char], at: usize) -> bool {
        match self {
            Self::Start => at == 0,
            Self::End => at == text.len() || (at + 1 == text.len() && text.last() == Some(&'\n')),
            Self::VeryEnd => at == text.len(),
            Self::Boundary | Self::NotBoundary => {
                let word = |at: Option<usize>| {
                    let c = at.and_then(|at| text.get(at));
                    c.is_some_and(|&c| Kind::Word.has(c))
                };
                let edge = word(at.checked_sub(1)) != word(Some(at));
                // An empty text has neither kind of place: `re` answers no to both.
                !text.is_empty() && edge == (self == Self::Boundary)
            }
        }
    }
}

/// A pattern as `re` parses it, as far as this port goes.
#[derive(Debug)]
enum Node {
    Literal(char),
    /// `.`: anything but a line break.
    Any,
    At(Place),
    Class(Class),
    /// `\1`: the text a group took.
    Same(usize),
    /// A group, with its number when it captures.
    Group(Option<usize>, Box<Node>),
    Sequence(Vec<Node>),
    Either(Vec<Node>),
    /// `*`, `+`, `?` and `{m,n}`: at least `min` rounds and at most `max`, as few as will do
    /// when `lazy`.
    Repeat {
        body: Box<Node>,
        min: u32,
        max: Option<u32>,
        lazy: bool,
    },
}

impl Node {
    /// The least number of characters the node takes. A reference to a group counts as none.
    fn least(&self) -> u64 {
        match self {
            Self::Literal(_) | Self::Any | Self::Class(_) => 1,
            Self::At(_) | Self::Same(_) => 0,
            Self::Group(_, body) => body.least(),
            Self::Sequence(items) => items
                .iter()
                .fold(0, |sum, item| sum.saturating_add(item.least())),
            Self::Either(branches) => branches.iter().map(Self::least).min().unwrap_or(0),
            Self::Repeat { body, min, .. } => u64::from(*min).saturating_mul(body.least()),
        }
    }

    /// For a node that can match without taking a character: how many rounds its loops have to
    /// go through to do so, at most. `None` for a node that always takes one.
    fn idle(&self) -> Option<u64> {
        match self {
            Self::Literal(_) | Self::Any | Self::Class(_) => None,
            Self::At(_) | Self::Same(_) => Some(0),
            Self::Group(_, body) => body.idle(),
            Self::Sequence(items) => items
                .iter()
                .try_fold(0_u64, |sum, item| Some(sum.saturating_add(item.idle()?))),
            Self::Either(branches) => branches.iter().filter_map(Self::idle).max(),
            Self::Repeat { body, min, .. } => match body.idle() {
                Some(inside) => Some(u64::from(*min).saturating_mul(inside.saturating_add(1))),
                None => (*min == 0).then_some(0),
            },
        }
    }
}

/// What `\d`, `\w`, `\s` and their opposites stand for.
fn category(letter: char) -> Option<Member> {
    let kind = match letter.to_ascii_lowercase() {
        'd' => Kind::Digit,
        'w' => Kind::Word,
        's' => Kind::Space,
        _ => return None,
    };
    Some(Member::Kind(kind, letter.is_ascii_lowercase()))
}

/// The characters `\n`, `\t` and the like stand for, by their letter.
fn control(letter: char) -> Option<char> {
    Some(match letter {
        'n' => '\n',
        't' => '\t',
        'r' => '\r',
        'f' => '\u{c}',
        'v' => '\u{b}',
        'a' => '\u{7}',
        _ => return None,
    })
}

struct Parser<'a> {
    rest: std::str::Chars<'a>,
    /// The named groups, with their numbers.
    names: Vec<(String, usize)>,
    /// How many capturing groups have been opened so far, and which of them are not closed yet.
    groups: usize,
    open: Vec<usize>,
    /// How many groups of any kind are open.
    depth: usize,
}

type Parsed<T> = Result<T, PatternError>;

impl Parser<'_> {
    fn peek(&self) -> Option<char> {
        self.rest.clone().next()
    }

    fn eat(&mut self, wanted: char) -> bool {
        let found = self.peek() == Some(wanted);
        if found {
            self.rest.next();
        }
        found
    }

    /// Alternatives up to a `)` or the end.
    fn alternatives(&mut self) -> Parsed<Node> {
        let mut branches = vec![self.sequence()?];
        while self.eat('|') {
            branches.push(self.sequence()?);
        }
        Ok(match branches.len() {
            1 => branches.remove(0),
            _ => Node::Either(branches),
        })
    }

    fn sequence(&mut self) -> Parsed<Node> {
        let mut items: Vec<Node> = Vec::new();
        while let Some(next) = self.peek().filter(|&c| c != '|' && c != ')') {
            self.rest.next();
            let item = match next {
                '*' => self.repeat(items.pop(), 0, None)?,
                '+' => self.repeat(items.pop(), 1, None)?,
                '?' => self.repeat(items.pop(), 0, Some(1))?,
                '{' => match self.counts()? {
                    Some((min, max)) => self.repeat(items.pop(), min, max)?,
                    None => Node::Literal('{'),
                },
                '.' => Node::Any,
                '^' => Node::At(Place::Start),
                '$' => Node::At(Place::End),
                '[' => Node::Class(self.class()?),
                '(' => self.group()?,
                '\\' => self.escape()?,
                literal => Node::Literal(literal),
            };
            items.push(item);
        }
        Ok(Node::Sequence(items))
    }

    /// The counts of a repeat like `{2}`, `{2,}`, `{,3}` or `{2,3}`, after its `{`. Anything
    /// else after a `{` leaves it an ordinary character, and nothing is read.
    fn counts(&mut self) -> Parsed<Option<(u32, Option<u32>)>> {
        let text = self.rest.as_str();
        if text.starts_with('}') {
            return Ok(None);
        }
        let digits = |text: &str| {
            let after = text.trim_start_matches(|c: char| c.is_ascii_digit());
            text.len() - after.len()
        };
        let (low, after) = text.split_at(digits(text));
        let (high, after) = match after.strip_prefix(',') {
            Some(after) => after.split_at(digits(after)),
            None => (low, after),
        };
        let Some(after) = after.strip_prefix('}') else {
            return Ok(None);
        };
        self.rest = after.chars();
        // Python reads the digits as a number of any size and then finds it too large, or finds
        // the digits too many to read at all. Neither is an error of the pattern.
        let count = |digits: &str| -> Parsed<Option<u32>> {
            if digits.is_empty() {
                return Ok(None);
            }
            let count = Some(digits).filter(|digits| digits.len() <= 10);
            let count = count.and_then(|digits| digits.parse().ok());
            let count = count.filter(|&count: &u32| count < TOO_MANY);
            let beyond = PatternError::Unsupported("a repeat count beyond what re takes");
            count.map(Some).ok_or(beyond)
        };
        let min = count(low)?.unwrap_or(0);
        let max = count(high)?;
        if max.is_some_and(|max| max < min) {
            return Err(PatternError::Bad("min repeat greater than max repeat"));
        }
        Ok(Some((min, max)))
    }

    /// A repeat of `body`, with a `?` after it for the lazy form.
    fn repeat(&mut self, body: Option<Node>, min: u32, max: Option<u32>) -> Parsed<Node> {
        let body = match body {
            None | Some(Node::At(_)) => return Err(PatternError::Bad("nothing to repeat")),
            Some(Node::Repeat { .. }) => return Err(PatternError::Bad("multiple repeat")),
            Some(body) => Box::new(body),
        };
        if self.peek() == Some('+') {
            return Err(PatternError::Unsupported("a possessive repeat such as *+"));
        }
        let lazy = self.eat('?');
        let repeat = Node::Repeat {
            body,
            min,
            max,
            lazy,
        };
        if repeat.idle().is_some_and(|rounds| rounds > IDLEST) {
            return Err(PatternError::Unsupported(
                "a loop that goes round very often without taking a character",
            ));
        }
        Ok(repeat)
    }

    fn group(&mut self) -> Parsed<Node> {
        // `None` for a group that captures nothing, `Some(None)` for one without a name.
        let name = if !self.eat('?') {
            Some(None)
        } else if self.eat(':') {
            None
        } else if self.eat('P') && self.eat('<') {
            Some(Some(self.group_name()?))
        } else {
            return Err(PatternError::Unsupported(
                "a group other than (...), (?:...) and (?P<name>...)",
            ));
        };
        let number = name.map(|name| {
            self.groups += 1;
            self.open.push(self.groups);
            self.names.extend(name.map(|name| (name, self.groups)));
            self.groups
        });
        self.depth += 1;
        if self.depth > DEEPEST {
            return Err(PatternError::Unsupported("groups nested very deep"));
        }
        let body = self.alternatives()?;
        if !self.eat(')') {
            return Err(PatternError::Bad("missing ), unterminated subpattern"));
        }
        self.depth -= 1;
        if number.is_some() {
            self.open.pop();
        }
        Ok(Node::Group(number, Box::new(body)))
    }

    fn group_name(&mut self) -> Parsed<String> {
        let mut name = String::new();
        loop {
            match self.rest.next() {
                None => return Err(PatternError::Bad("missing >, unterminated name")),
                Some('>') => break,
                Some(c) => name.push(c),
            }
        }
        let mut letters = name.chars();
        let plain = letters
            .next()
            .is_some_and(|c| c.is_ascii_alphabetic() || c == '_')
            && letters.all(|c| c.is_ascii_alphanumeric() || c == '_');
        if name.is_empty() {
            return Err(PatternError::Bad("missing group name"));
        }
        if !plain {
            return Err(PatternError::Unsupported(
                "a group name that is not plain ASCII",
            ));
        }
        if self.names.iter().any(|(known, _)| *known == name) {
            return Err(PatternError::Bad("redefinition of group name"));
        }
        Ok(name)
    }

    /// What follows a backslash outside a class.
    fn escape(&mut self) -> Parsed<Node> {
        let Some(c) = self.rest.next() else {
            return Err(PatternError::Bad("bad escape (end of pattern)"));
        };
        if let Some(member) = category(c) {
            let (negated, members) = (false, vec![member]);
            return Ok(Node::Class(Class { negated, members }));
        }
        if let Some(literal) = control(c) {
            return Ok(Node::Literal(literal));
        }
        match c {
            'A' => Ok(Node::At(Place::Start)),
            'Z' => Ok(Node::At(Place::VeryEnd)),
            'b' => Ok(Node::At(Place::Boundary)),
            'B' => Ok(Node::At(Place::NotBoundary)),
            'x' | 'u' | 'U' => self.numbered(c).map(Node::Literal),
            'N' => Err(PatternError::Unsupported("a character written by its name")),
            '0' => self.octal(c, 2).map(Node::Literal),
            '1'..='9' => self.reference(c),
            c if c.is_ascii_alphabetic() => Err(PatternError::Bad("bad escape")),
            literal => Ok(Node::Literal(literal)),
        }
    }

    /// `\x41`, `é`, `\U0001f600`: a character by its number, with exactly as many hex
    /// digits as the letter asks for.
    fn numbered(&mut self, letter: char) -> Parsed<char> {
        let wanted = match letter {
            'x' => 2,
            'u' => 4,
            _ => 8,
        };
        let mut digits = String::new();
        while digits.len() < wanted {
            match self.peek().filter(char::is_ascii_hexdigit) {
                Some(digit) => digits.push(digit),
                None => return Err(PatternError::Bad("incomplete escape")),
            }
            self.rest.next();
        }
        let code = u32::from_str_radix(&digits, 16)
            .ok()
            .filter(|&code| code <= 0x10_ffff);
        let code = code.ok_or(PatternError::Bad("bad escape"))?;
        // Python can hold half of a surrogate pair as a character; text here never has one.
        char::from_u32(code).ok_or(PatternError::Unsupported("a lone surrogate"))
    }

    /// An octal escape: the digit already read and up to `more` further octal digits.
    fn octal(&mut self, first: char, more: usize) -> Parsed<char> {
        let mut digits = String::from(first);
        while digits.len() <= more {
            match self.peek().filter(|c| ('0'..='7').contains(c)) {
                Some(digit) => digits.push(digit),
                None => break,
            }
            self.rest.next();
        }
        let code = u32::from_str_radix(&digits, 8)
            .ok()
            .filter(|&code| code <= 0o377);
        let literal = code.and_then(char::from_u32);
        literal.ok_or(PatternError::Bad("octal escape value outside of range"))
    }

    /// A backslash and a digit: a reference to a group, unless three octal digits follow each
    /// other. The group has to be there already, and closed.
    fn reference(&mut self, first: char) -> Parsed<Node> {
        let mut digits = String::from(first);
        if let Some(second) = self.peek().filter(char::is_ascii_digit) {
            self.rest.next();
            digits.push(second);
            let octal = |c: char| ('0'..='7').contains(&c);
            if let Some(third) = self
                .peek()
                .filter(|&c| octal(first) && octal(second) && octal(c))
            {
                self.rest.next();
                digits.push(third);
                let code = u32::from_str_radix(&digits, 8)
                    .ok()
                    .filter(|&code| code <= 0o377);
                let literal = code.and_then(char::from_u32).map(Node::Literal);
                return literal.ok_or(PatternError::Bad("octal escape value outside of range"));
            }
        }
        let group: usize = digits.parse().unwrap_or(usize::MAX);
        if group > self.groups {
            Err(PatternError::Bad("invalid group reference"))
        } else if self.open.contains(&group) {
            Err(PatternError::Bad("cannot refer to an open group"))
        } else {
            Ok(Node::Same(group))
        }
    }

    /// One member of a class: a character, or a category such as `\d`.
    fn class_member(&mut self, first: char) -> Parsed<Member> {
        if first != '\\' {
            return Ok(Member::One(first));
        }
        let Some(c) = self.rest.next() else {
            return Err(PatternError::Bad("unterminated character set"));
        };
        if let Some(member) = category(c) {
            return Ok(member);
        }
        if let Some(literal) = control(c) {
            return Ok(Member::One(literal));
        }
        match c {
            'b' => Ok(Member::One('\u{8}')),
            'x' | 'u' | 'U' => self.numbered(c).map(Member::One),
            'N' => Err(PatternError::Unsupported("a character written by its name")),
            // In a class a digit can only be octal.
            '0'..='7' => self.octal(c, 2).map(Member::One),
            '8' | '9' => Err(PatternError::Bad("bad escape")),
            c if c.is_ascii_alphabetic() => Err(PatternError::Bad("bad escape")),
            literal => Ok(Member::One(literal)),
        }
    }

    /// A class after its `[`. A `]` right at the start is a member, and so is a `-` that has
    /// nothing on one side.
    fn class(&mut self) -> Parsed<Class> {
        let unterminated = PatternError::Bad("unterminated character set");
        let negated = self.eat('^');
        let mut members = Vec::new();
        loop {
            let first = self.rest.next().ok_or(unterminated.clone())?;
            if first == ']' && !members.is_empty() {
                break;
            }
            let low = self.class_member(first)?;
            if !self.eat('-') {
                members.push(low);
                continue;
            }
            let second = self.rest.next().ok_or(unterminated.clone())?;
            if second == ']' {
                members.extend([low, Member::One('-')]);
                break;
            }
            match (low, self.class_member(second)?) {
                (Member::One(low), Member::One(high)) if low <= high => {
                    members.push(Member::Range(low, high));
                }
                _ => return Err(PatternError::Bad("bad character range")),
            }
        }
        Ok(Class { negated, members })
    }
}

/// One step of a compiled pattern. Steps run in order unless one says where to go.
#[derive(Clone, Debug)]
enum Step {
    Char(char),
    Any,
    Class(Class),
    At(Place),
    Same(usize),
    /// Notes where a group starts (an even number) or ends (the odd one after it).
    Mark(usize),
    /// Goes on, and comes back to the step named here if that leads nowhere.
    Either(usize),
    Jump(usize),
    /// Starts a loop: no round done yet.
    Enter(usize),
    /// Decides between another round, which starts at the next step, and leaving for `exit`.
    Until {
        slot: usize,
        min: u32,
        max: Option<u32>,
        lazy: bool,
        exit: usize,
    },
    /// The end of a round: back to the `Until` of the loop.
    Again {
        slot: usize,
        until: usize,
    },
    Match,
}

/// Writes the steps for a node after the ones that are there. `loops` counts the loops.
fn compile(node: &Node, steps: &mut Vec<Step>, loops: &mut usize) {
    // A step that names a later one is written with 0 first and set once that one is known.
    let set = |steps: &mut Vec<Step>, at: usize, step: Step| {
        if let Some(slot) = steps.get_mut(at) {
            *slot = step;
        }
    };
    match node {
        Node::Literal(c) => steps.push(Step::Char(*c)),
        Node::Any => steps.push(Step::Any),
        Node::At(place) => steps.push(Step::At(*place)),
        Node::Class(class) => steps.push(Step::Class(class.clone())),
        Node::Same(group) => steps.push(Step::Same(*group)),
        Node::Group(number, body) => {
            // Group 1 has the marks 0 and 1, group 2 the marks 2 and 3.
            let start = number.map(|number| 2 * number.saturating_sub(1));
            steps.extend(start.map(Step::Mark));
            compile(body, steps, loops);
            steps.extend(start.map(|start| Step::Mark(start + 1)));
        }
        Node::Sequence(items) => {
            for item in items {
                compile(item, steps, loops);
            }
        }
        Node::Either(branches) => {
            let mut ends = Vec::new();
            for (at, branch) in branches.iter().enumerate() {
                if at + 1 == branches.len() {
                    compile(branch, steps, loops);
                    break;
                }
                let fork = steps.len();
                steps.push(Step::Either(0));
                compile(branch, steps, loops);
                ends.push(steps.len());
                steps.push(Step::Jump(0));
                let next = steps.len();
                set(steps, fork, Step::Either(next));
            }
            let end = steps.len();
            for jump in ends {
                set(steps, jump, Step::Jump(end));
            }
        }
        &Node::Repeat {
            ref body,
            min,
            max,
            lazy,
        } => {
            let slot = *loops;
            *loops += 1;
            steps.push(Step::Enter(slot));
            let until = steps.len();
            steps.push(Step::Jump(0));
            compile(body, steps, loops);
            steps.push(Step::Again { slot, until });
            let exit = steps.len();
            let decide = Step::Until {
                slot,
                min,
                max,
                lazy,
                exit,
            };
            set(steps, until, decide);
        }
    }
}

/// Where a loop stands: the rounds done, and where the latest round beyond the least number
/// of them started.
#[derive(Clone, Copy, Debug, Default)]
struct Loop {
    rounds: u64,
    last: Option<usize>,
}

impl Loop {
    /// Whether another round may start at `at`, once the least number of rounds is done: only
    /// below `max`, and only if the text has moved on since the last round started.
    fn may_go_on(&self, max: Option<u32>, at: usize) -> bool {
        max.is_none_or(|max| self.rounds < u64::from(max)) && self.last != Some(at)
    }
}

/// What a step changed, to put back when the way it was on leads nowhere.
#[derive(Clone, Copy, Debug)]
enum Change {
    Mark(usize, Option<usize>),
    Loop(usize, Loop),
}

/// Something left to try: the step to go on from, where in the text, and how many changes had
/// been made by then. `more` is a lazy loop that left and may come back for another round.
#[derive(Clone, Copy, Debug)]
struct Choice {
    step: usize,
    at: usize,
    changes: usize,
    more: bool,
}

/// Where a group starts and ends, if it took part.
fn span(marks: &[Option<usize>], group: usize) -> Option<(usize, usize)> {
    let start = 2 * group.checked_sub(1)?;
    Some(((*marks.get(start)?)?, (*marks.get(start + 1)?)?))
}

/// A compiled pattern: what `re.compile` returns.
#[derive(Clone, Debug)]
pub struct Pattern {
    steps: Vec<Step>,
    loops: usize,
    groups: usize,
    names: Vec<(String, usize)>,
    /// The least number of characters a match takes.
    least: u64,
}

/// A match: what `re.match` returns.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Found {
    /// Where the match ends, in characters from the start of the text. It starts at 0.
    pub end: usize,
    /// `groups()`: the text of each group, `None` for one that took no part.
    pub groups: Vec<Option<String>>,
    /// `groupdict()`: the named groups, in the order they are written.
    pub named: Vec<(String, Option<String>)>,
}

impl Pattern {
    /// `re.compile(pattern)`, for the part of `re` this port reads.
    pub fn new(pattern: &str) -> Result<Self, PatternError> {
        let mut parser = Parser {
            rest: pattern.chars(),
            names: Vec::new(),
            groups: 0,
            open: Vec::new(),
            depth: 0,
        };
        let parsed = parser.alternatives()?;
        if parser.peek().is_some() {
            return Err(PatternError::Bad("unbalanced parenthesis"));
        }
        let (mut steps, mut loops) = (Vec::new(), 0);
        compile(&parsed, &mut steps, &mut loops);
        steps.push(Step::Match);
        Ok(Self {
            steps,
            loops,
            groups: parser.groups,
            names: parser.names,
            least: parsed.least(),
        })
    }

    /// `pattern.match(text)`: the pattern at the start of the text.
    ///
    /// Like `re`, this tries one way after the other, so a pattern such as `(a+)+b` takes time
    /// that doubles with every `a` of a text that has no `b`.
    pub fn match_start(&self, text: &str) -> Option<Found> {
        let text: Vec<char> = text.chars().collect();
        let (end, marks) = self.run(&text)?;
        let group = |number: usize| {
            let (from, to) = span(&marks, number)?;
            Some(text.get(from..to)?.iter().collect::<String>())
        };
        let named = |(name, number): &(String, usize)| (name.clone(), group(*number));
        Some(Found {
            end,
            groups: (1..=self.groups).map(group).collect(),
            named: self.names.iter().map(named).collect(),
        })
    }

    /// Where the match ends and what the marks of the groups are, or `None` for no match.
    ///
    /// This follows `SRE(match)` of CPython's `Modules/_sre/sre_lib.h`. Its loops are the part
    /// to get right. A greedy loop goes for another round first and leaves when that leads
    /// nowhere; a lazy one leaves first. Either starts a round only below `max` and, once `min`
    /// rounds are done, only if the text has moved on since the round before started: a round
    /// that took nothing is the last. A way that leads nowhere puts back every group and loop
    /// it changed.
    fn run(&self, text: &[char]) -> Option<(usize, Vec<Option<usize>>)> {
        // A text too short for the pattern is not tried at all. `re` does the same, and it is
        // what keeps `(a*)*b.{500}` from trying every way through a short text first.
        if u64::try_from(text.len()).is_ok_and(|length| length < self.least) {
            return None;
        }
        let mut marks: Vec<Option<usize>> = vec![None; 2 * self.groups];
        let mut loops = vec![Loop::default(); self.loops];
        let mut changes: Vec<Change> = Vec::new();
        let mut choices: Vec<Choice> = Vec::new();
        let (mut step, mut at) = (0, 0);
        loop {
            let mut alive = true;
            match self.steps.get(step)? {
                Step::Match => return Some((at, marks)),
                Step::Char(wanted) => {
                    alive = text.get(at) == Some(wanted);
                    (step, at) = (step + 1, at + 1);
                }
                Step::Any => {
                    alive = text.get(at).is_some_and(|&c| c != '\n');
                    (step, at) = (step + 1, at + 1);
                }
                Step::Class(class) => {
                    alive = text.get(at).is_some_and(|&c| class.has(c));
                    (step, at) = (step + 1, at + 1);
                }
                Step::At(place) => {
                    alive = place.holds(text, at);
                    step += 1;
                }
                Step::Same(group) => {
                    let taken = span(&marks, *group).and_then(|(from, to)| text.get(from..to));
                    let length = taken.map_or(0, <[char]>::len);
                    alive = taken.is_some() && taken == text.get(at..at + length);
                    (step, at) = (step + 1, at + length);
                }
                Step::Mark(mark) => {
                    let slot = marks.get_mut(*mark)?;
                    changes.push(Change::Mark(*mark, *slot));
                    *slot = Some(at);
                    step += 1;
                }
                Step::Either(other) => {
                    choices.push(Choice {
                        step: *other,
                        at,
                        changes: changes.len(),
                        more: false,
                    });
                    step += 1;
                }
                Step::Jump(to) => step = *to,
                Step::Enter(slot) => {
                    let state = loops.get_mut(*slot)?;
                    changes.push(Change::Loop(*slot, *state));
                    *state = Loop::default();
                    step += 1;
                }
                Step::Again { slot, until } => {
                    let state = loops.get_mut(*slot)?;
                    changes.push(Change::Loop(*slot, *state));
                    state.rounds += 1;
                    step = *until;
                }
                &Step::Until {
                    slot,
                    min,
                    max,
                    lazy,
                    exit,
                } => {
                    let state = loops.get_mut(slot)?;
                    let mut choice = Choice {
                        step: exit,
                        at,
                        changes: changes.len(),
                        more: false,
                    };
                    if state.rounds < u64::from(min) {
                        step += 1;
                    } else if lazy {
                        (choice.step, choice.more) = (step, true);
                        choices.push(choice);
                        step = exit;
                    } else if state.may_go_on(max, at) {
                        choices.push(choice);
                        changes.push(Change::Loop(slot, *state));
                        state.last = Some(at);
                        step += 1;
                    } else {
                        step = exit;
                    }
                }
            }
            while !alive {
                let choice = choices.pop()?;
                while changes.len() > choice.changes {
                    match changes.pop()? {
                        Change::Mark(mark, old) => *marks.get_mut(mark)? = old,
                        Change::Loop(slot, old) => *loops.get_mut(slot)? = old,
                    }
                }
                (step, at, alive) = (choice.step, choice.at, true);
                if choice.more {
                    // The lazy loop at this step left, and that led nowhere: one more round, if
                    // it may.
                    let Some(&Step::Until { slot, max, .. }) = self.steps.get(step) else {
                        return None;
                    };
                    let state = loops.get_mut(slot)?;
                    alive = state.may_go_on(max, at);
                    if alive {
                        changes.push(Change::Loop(slot, *state));
                        state.last = Some(at);
                        step += 1;
                    }
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn found(pattern: &str, text: &str) -> Option<(usize, Vec<Option<String>>)> {
        let compiled = Pattern::new(pattern).unwrap();
        compiled
            .match_start(text)
            .map(|found| (found.end, found.groups))
    }

    fn groups(items: &[Option<&str>]) -> Vec<Option<String>> {
        items.iter().map(|item| item.map(str::to_string)).collect()
    }

    #[test]
    fn the_handler_goes_in_front() {
        assert_eq!(command_pattern("ping$", "."), "\\.ping$");
        assert_eq!(command_pattern("^.ping", "."), "\\.ping");
        assert_eq!(command_pattern("^^ping", "!"), "\\!^ping");
        assert_eq!(command_pattern("..ping", "/"), "\\/.ping");
        assert_eq!(command_pattern(".ping", " "), "^ping");
        assert_eq!(command_pattern("ping", "NO_HNDLR"), "^ping");
        // The backslash escapes only the first character of the handler.
        assert_eq!(command_pattern("ping", ".."), "\\..ping");
        assert_eq!(command_pattern("ping", "d"), "\\dping");
        assert_eq!(assistant_pattern("start( (.*)|$)"), "^/start( (.*)|$)");
    }

    // The expected values of every test below are what CPython 3.11 answers for
    // `re.compile(pattern).match(text)`.

    #[test]
    fn commands_match_as_in_python() {
        let ban = "\\.ban( (.*)|$)";
        assert_eq!(found(ban, ".ban"), Some((4, groups(&[Some(""), None]))));
        assert_eq!(
            found(ban, ".ban @user spam"),
            Some((15, groups(&[Some(" @user spam"), Some("@user spam")])))
        );
        assert_eq!(found(ban, ".banana"), None);
        assert_eq!(found(ban, " .ban"), None);
        // `$` also matches before a line break that ends the text, and the match stops there.
        assert_eq!(found(ban, ".ban\n"), Some((4, groups(&[Some(""), None]))));
        assert_eq!(found(ban, ".ban\n\n"), None);
        assert_eq!(found("\\.ping$", ".ping\n"), Some((5, vec![])));
        // `.` stops at a line break.
        assert_eq!(
            found(ban, ".ban a\nb"),
            Some((6, groups(&[Some(" a"), Some("a")])))
        );
        assert_eq!(
            found("\\.(un|)lock( (.*)|$)", ".lock"),
            Some((5, groups(&[Some(""), Some(""), None])))
        );
        assert_eq!(
            found("\\.setname ?((.|//)*)", ".setname ab"),
            Some((11, groups(&[Some("ab"), Some("b")])))
        );
        assert_eq!(
            found("\\.sg(|u)(?:\\s|$)([\\s\\S]*)", ".sgu\nx\ny"),
            Some((8, groups(&[Some("u"), Some("x\ny")])))
        );
        assert_eq!(
            found("\\.setflood ?(\\d+)", ".setflood ٣٤x"),
            Some((12, groups(&[Some("٣٤")])))
        );
        assert_eq!(found("^ping", "ping"), Some((4, vec![])));
        assert_eq!(
            found("^/start( (.*)|$)", "/start x"),
            Some((8, groups(&[Some(" x"), Some("x")])))
        );
    }

    #[test]
    fn python_classes() {
        // `\w` is letters, digits of every kind and the underscore, but no combining mark.
        assert_eq!(found("\\w+", "aé_٣²e\u{301}"), Some((6, vec![])));
        assert_eq!(found("\\s+", " \t\u{1f}\u{a0}\u{3000}x"), Some((5, vec![])));
        assert_eq!(found("[^\\d]+", "ab1"), Some((2, vec![])));
        assert_eq!(found("[]a-c-]+", "a]-bd"), Some((4, vec![])));
        assert_eq!(found("[\\]\\\\^-]+", "]\\^-a"), Some((4, vec![])));
        assert_eq!(found("[^\\W\\d]+", "aé_1"), Some((3, vec![])));
        assert_eq!(found("a{b}{2,x}", "a{b}{2,x}"), Some((9, vec![])));
    }

    #[test]
    fn named_groups() {
        let compiled = Pattern::new("(?P<name>\\w+) (?P<rest>.*)(?P<none>x)?").unwrap();
        let found = compiled.match_start("ping now").unwrap();
        assert_eq!(found.groups, groups(&[Some("ping"), Some("now"), None]));
        let named = [
            ("name".to_string(), Some("ping".to_string())),
            ("rest".to_string(), Some("now".to_string())),
            ("none".to_string(), None),
        ];
        assert_eq!(found.named, named);
    }

    #[test]
    fn what_python_refuses() {
        for pattern in [
            "*a",
            "a**",
            "a|*",
            "(",
            "(a",
            "a)",
            "[a",
            "[z-a]",
            "[\\d-a]",
            "\\",
            "\\c",
            "^*",
            "$+",
            "(?P<a>x)(?P<a>y)",
            "(?P<a",
            "(?P<>a)",
            "\\ping",
            "\\1",
            "\\1ping",
            "(a)\\2",
            "(a)\\10",
            "(a\\1)",
            "\\b*",
            "a{2,1}",
            "{2}",
            "^{2}",
            "a{2}{3}",
            "a{2}*",
            "a{2}??",
            "a*?*",
        ] {
            let refused = matches!(Pattern::new(pattern), Err(PatternError::Bad(_)));
            assert!(refused, "{pattern:?}");
        }
    }

    #[test]
    fn what_is_left_alone() {
        let deep = format!("{}a{}", "(".repeat(101), ")".repeat(101));
        for pattern in [
            "(?=a)",
            "(?i)a",
            "a*+",
            "a{2}+",
            "(?>a)",
            "(?P<n>a)(?P=n)",
            "\\N{DASH}",
            "\\ud83d",
            "(?P<é>a)",
            "(?#x)",
            // Python raises an OverflowError for these, which is not `re.error`.
            "a{4294967295}",
            "a{2,99999999999999999999}",
            "a{00000000002}",
            // Rounds that take nothing, more of them than anyone can wait for.
            "(a?){100001}",
            "((a?){400}){400}",
            "(?:(?:){400}){400}",
            &deep,
        ] {
            let left = matches!(Pattern::new(pattern), Err(PatternError::Unsupported(_)));
            assert!(left, "{pattern:?}");
        }
        assert!(Pattern::new(&deep[1..deep.len() - 1]).is_ok());
        assert!(Pattern::new("a{4294967294}").is_ok());
        assert!(Pattern::new("(a?){100000}").is_ok());
        assert!(Pattern::new("((a?){300}){300}").is_ok());
        assert!(Pattern::new("(a?|b){0,4294967294}").is_ok());
        assert_eq!(found("(a?){1000}b", "aab"), Some((3, groups(&[Some("")]))));
    }

    #[test]
    fn a_round_that_takes_nothing_is_the_last() {
        assert_eq!(found("(a*)*", "aa"), Some((2, groups(&[Some("")]))));
        assert_eq!(found("(a*)+", "aa"), Some((2, groups(&[Some("")]))));
        assert_eq!(found("(?:|a)*", "aa"), Some((0, vec![])));
        assert_eq!(found("(|a)*b", "aab"), Some((3, groups(&[Some("")]))));
        assert_eq!(found("(a|b*)*", "abb"), Some((3, groups(&[Some("")]))));
        assert_eq!(found("(?:b*|a)*", "a"), Some((0, vec![])));
        assert_eq!(found("(a??)*b", "aab"), Some((3, groups(&[Some("")]))));
        assert_eq!(found("(?:\\s??#*)+", " #"), Some((0, vec![])));
        assert_eq!(found("(a{0,2})*", "aaaaa"), Some((5, groups(&[Some("")]))));
        assert_eq!(found("(?:a|)*b", "aab"), Some((3, vec![])));
        assert_eq!(found("(?:)*a(?:$)+", "a\n"), Some((1, vec![])));
        assert_eq!(found("(?:^)?a(?:$)*b", "ab"), Some((2, vec![])));
    }

    #[test]
    fn lazy_and_greedy_loops() {
        assert_eq!(found("(a+?)*", "aaaa"), Some((4, groups(&[Some("a")]))));
        assert_eq!(found("(a+?)*b", "aaaab"), Some((5, groups(&[Some("a")]))));
        assert_eq!(found("(a*)*?b", "aab"), Some((3, groups(&[Some("aa")]))));
        assert_eq!(found("(a*?)+?b", "aab"), Some((3, groups(&[Some("a")]))));
        assert_eq!(
            found("\\\\*([]x]+[abc]*)*?\\\\*", "\\\\]x\\"),
            Some((2, groups(&[None])))
        );
        assert_eq!(found("x(.+?)*y", "xaby"), Some((4, groups(&[Some("b")]))));
        // A group keeps what it took in an earlier round when a later round goes another way.
        assert_eq!(found("(?:(a)|b)*", "ab"), Some((2, groups(&[Some("a")]))));
        assert_eq!(
            found("(?:(a)|(b))*", "ab"),
            Some((2, groups(&[Some("a"), Some("b")])))
        );
        assert_eq!(
            found("(a|ab)(c|bcd)(d*)", "abcd"),
            Some((4, groups(&[Some("a"), Some("bcd"), Some("")])))
        );
    }

    #[test]
    fn a_text_too_short_is_not_tried() {
        // Without the look at the length first, the loops in front would be tried every way.
        let pattern = "(\\S*?-*)+?(b{2,3}?\\[+){3}.{100001}";
        assert_eq!(found(pattern, "_11_--1--bb[[bb[bbb[[[1 éaa"), None);
        assert_eq!(found("(a*)*b.{500}", &"a".repeat(400)), None);
        assert_eq!(found("a{3}", "aa"), None);
        assert_eq!(found("(a)\\1{3}b|c", "c"), Some((1, groups(&[None]))));
        assert_eq!(found("(?:a{2}|b)c", "bc"), Some((2, vec![])));
    }

    #[test]
    fn counted_repeats() {
        assert_eq!(
            found("(a{2}){1,2}", "aaaaaa"),
            Some((4, groups(&[Some("aa")])))
        );
        assert_eq!(found("(a?){3}", "a"), Some((1, groups(&[Some("")]))));
        assert_eq!(found("(a?){2,3}?", "aaaa"), Some((2, groups(&[Some("a")]))));
        assert_eq!(found("(?:a{2}){3}", "aaaaaaa"), Some((6, vec![])));
        assert_eq!(found("a{,2}", "aaa"), Some((2, vec![])));
        assert_eq!(found("a{2,}?", "aaaa"), Some((2, vec![])));
        assert_eq!(found("a{0}b", "b"), Some((1, vec![])));
        assert_eq!(found("a{2}", "a"), None);
        assert_eq!(found("a{,}b", "aaab"), Some((4, vec![])));
        // A `{` that starts no count is an ordinary character.
        assert_eq!(found("x{1}{", "x{"), Some((2, vec![])));
        assert_eq!(found("a{1,2}{", "aa{"), Some((3, vec![])));
        assert_eq!(found("a{1,2,3}", "a{1,2,3}"), Some((8, vec![])));
        assert_eq!(found("a{ 1}", "a{ 1}"), Some((5, vec![])));
        assert_eq!(found("a{١}", "a{١}"), Some((4, vec![])));
    }

    #[test]
    fn the_text_of_a_group_again() {
        assert_eq!(found("(a)\\1", "aa"), Some((2, groups(&[Some("a")]))));
        assert_eq!(found("(a)\\1", "ab"), None);
        assert_eq!(found("(a|b)\\1+", "bbba"), Some((3, groups(&[Some("b")]))));
        assert_eq!(found("(a*)\\1", "aaaa"), Some((4, groups(&[Some("aa")]))));
        assert_eq!(
            found("(.)(.)\\2\\1", "abba!"),
            Some((4, groups(&[Some("a"), Some("b")])))
        );
        assert_eq!(found("()\\1x", "x"), Some((1, groups(&[Some("")]))));
        // A group that took no part matches nothing, not the empty text.
        assert_eq!(found("(a)?\\1", "x"), None);
        assert_eq!(found("(?:(a)|b)\\1", "ba"), None);
        assert_eq!(found("(a)(b)?\\2", "ab"), None);
    }

    #[test]
    fn characters_by_number() {
        assert_eq!(
            found("\\x41\\u00e9\\U0001f600\\0\\101\\08", "Aé😀\0A\u{0}8"),
            Some((7, vec![]))
        );
        assert_eq!(
            found("[\\x41-\\x43\\101\\7]+", "ABC\u{7}D"),
            Some((4, vec![]))
        );
        // A handler that is a digit: `\0` is the NUL character, `\1` a group that is not there.
        assert_eq!(
            found(&command_pattern("ping", "0"), "\0ping"),
            Some((5, vec![]))
        );
        for pattern in [
            "\\x4",
            "\\xg1",
            "\\u00e",
            "\\U00110000",
            "\\400",
            "[\\8]",
            "[\\400]",
            "\\xping",
        ] {
            let refused = matches!(Pattern::new(pattern), Err(PatternError::Bad(_)));
            assert!(refused, "{pattern:?}");
        }
    }

    #[test]
    fn edges_of_words_and_of_the_text() {
        // A handler that is a letter is read as an escape: `b` makes `\bping`.
        let ping = command_pattern("ping( (.*)|$)", "b");
        assert_eq!(
            found(&ping, "ping x"),
            Some((6, groups(&[Some(" x"), Some("x")])))
        );
        assert_eq!(found(&ping, "bping"), None);
        assert_eq!(found("a\\b", "a b"), Some((1, vec![])));
        assert_eq!(found("a\\b", "ab"), None);
        assert_eq!(found("a\\B", "ab"), Some((1, vec![])));
        assert_eq!(found("a\\B", "a b"), None);
        assert_eq!(found("a\\B", "a"), None);
        assert_eq!(found("\\Bé", "é"), None);
        assert_eq!(found("\\B-", "-"), Some((1, vec![])));
        assert_eq!(found("\\b", "a"), Some((0, vec![])));
        // In an empty text there is neither the edge of a word nor a place that is not one.
        assert_eq!(found("\\b", ""), None);
        assert_eq!(found("\\B", ""), None);
        assert_eq!(found("x*\\B", ""), None);
        assert_eq!(found("\\Aa\\Z", "a"), Some((1, vec![])));
        // `\Z` is the very end; `$` also takes the place before a last line break.
        assert_eq!(found("a\\Z", "a\n"), None);
        assert_eq!(found("a$", "a\n"), Some((1, vec![])));
        assert_eq!(found("$", ""), Some((0, vec![])));
        assert_eq!(found("$", "\n"), Some((0, vec![])));
        assert_eq!(found("^$\\n", "\n"), Some((1, vec![])));
    }
}
