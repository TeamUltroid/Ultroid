//! `ast.literal_eval`, as CPython 3.11 applies it to stored text.
//!
//! Every value the database reads goes through this, so it accepts exactly the text CPython
//! accepts: Python's own tokenizer rules for numbers, strings, comments and line joining, and
//! only the expressions `literal_eval` allows. Anything else is not a literal, and the database
//! keeps such text as it is. The reason is never needed, so there is no error type.

use crate::repr::MAX_INT_DIGITS;
use crate::tables::{ALIASES, UNASSIGNED};
use crate::value::{PyDict, PySet, PyValue};
use num_bigint::BigInt;
use num_traits::Num;
use unicode_normalization::UnicodeNormalization;

/// The deepest bracket nesting CPython's tokenizer accepts.
const MAX_NESTING: usize = 200;

struct NotLiteral;
type Parsed<T> = Result<T, NotLiteral>;

enum Piece {
    /// Code points, so that an escape like `\ud83d` can stand for a lone surrogate.
    Str(Vec<u32>),
    Bytes(Vec<u8>),
}

enum Token {
    Number(PyValue),
    Text(Piece),
    /// `True`, `False` or `None`.
    Constant(PyValue),
    /// The name `set`, which is only a literal when called with no arguments.
    SetName,
    Ellipsis,
    Symbol(char),
    Newline,
    End,
}

/// What an expression is to `literal_eval`: it decides what a sign or a `+ 2j` may attach to.
enum Node {
    /// An int, float or imaginary number as written.
    Number(PyValue),
    /// One `+` or `-` applied to a number as written.
    Signed(PyValue),
    Value(PyValue),
    SetName,
}

impl Node {
    fn value(self) -> Parsed<PyValue> {
        match self {
            Self::Number(value) | Self::Signed(value) | Self::Value(value) => Ok(value),
            Self::SetName => Err(NotLiteral),
        }
    }
}

#[derive(Default)]
struct Prefix {
    bytes: bool,
    raw: bool,
    format: bool,
}

fn is_name_char(c: char) -> bool {
    c == '_' || c.is_ascii_alphanumeric() || !c.is_ascii()
}

/// The character with this exact name. The names crate matches loosely (`EMDASH` finds
/// `EM DASH`) and knows a newer Unicode, so its answer is checked against the name it reports
/// and against the characters CPython's Unicode version has.
fn character_by_name(name: &str) -> Option<char> {
    let found = unicode_names2::character(name)?;
    let exact = unicode_names2::name(found)?.to_string();
    let computed = ["CJK UNIFIED IDEOGRAPH-", "HANGUL SYLLABLE "]
        .iter()
        .any(|prefix| exact.starts_with(prefix));
    let same = if computed {
        exact == name
    } else {
        exact.eq_ignore_ascii_case(name)
    };
    let code = u32::from(found);
    let assigned = !UNASSIGNED
        .iter()
        .any(|&(first, last)| (first..=last).contains(&code));
    (same && assigned).then_some(found)
}

/// The character `\N{name}` stands for: a name or an alias, matched without regard to case
/// except for the computed names of CJK ideographs and Hangul syllables.
fn named_character(name: &str) -> Option<char> {
    if !name.is_ascii() {
        return None;
    }
    character_by_name(name).or_else(|| {
        let upper = name.to_ascii_uppercase();
        let at = ALIASES
            .binary_search_by(|(alias, _)| (*alias).cmp(upper.as_str()))
            .ok()?;
        char::from_u32(ALIASES[at].1)
    })
}

fn hex(body: &[char], at: &mut usize, digits: usize) -> Parsed<u32> {
    let mut value = 0;
    for _ in 0..digits {
        let digit = body
            .get(*at)
            .and_then(|c| c.to_digit(16))
            .ok_or(NotLiteral)?;
        value = value * 16 + digit;
        *at += 1;
    }
    Ok(value)
}

fn octal(first: char, body: &[char], at: &mut usize) -> u32 {
    let mut value = first.to_digit(8).unwrap_or(0);
    for _ in 0..2 {
        let Some(digit) = body.get(*at).and_then(|c| c.to_digit(8)) else {
            break;
        };
        value = value * 8 + digit;
        *at += 1;
    }
    value
}

/// The escapes `str` and `bytes` literals share. `None` for anything else.
fn simple_escape(c: char) -> Option<u32> {
    Some(match c {
        '\\' | '\'' | '"' => u32::from(c),
        'a' => 7,
        'b' => 8,
        'f' => 12,
        'n' => 10,
        'r' => 13,
        't' => 9,
        'v' => 11,
        _ => return None,
    })
}

fn unescape_str(body: &[char]) -> Parsed<Vec<u32>> {
    let mut out = Vec::with_capacity(body.len());
    let mut at = 0;
    while let Some(&c) = body.get(at) {
        at += 1;
        if c != '\\' {
            out.push(u32::from(c));
            continue;
        }
        let escaped = *body.get(at).ok_or(NotLiteral)?;
        at += 1;
        match escaped {
            '\n' => {}
            '0'..='7' => out.push(octal(escaped, body, &mut at)),
            'x' => out.push(hex(body, &mut at, 2)?),
            'u' => out.push(hex(body, &mut at, 4)?),
            'U' => out.push(
                Some(hex(body, &mut at, 8)?)
                    .filter(|&code| code <= 0x10ffff)
                    .ok_or(NotLiteral)?,
            ),
            'N' => {
                let close = (at..body.len())
                    .find(|&i| body[i] == '}')
                    .ok_or(NotLiteral)?;
                if body.get(at) != Some(&'{') || close == at + 1 {
                    return Err(NotLiteral);
                }
                let name: String = body[at + 1..close].iter().collect();
                out.push(u32::from(named_character(&name).ok_or(NotLiteral)?));
                at = close + 1;
            }
            other => match simple_escape(other) {
                Some(code) => out.push(code),
                // An unknown escape stays as written, backslash included.
                None => out.extend([u32::from('\\'), u32::from(other)]),
            },
        }
    }
    Ok(out)
}

fn unescape_bytes(body: &[char]) -> Parsed<Vec<u8>> {
    let mut out = Vec::with_capacity(body.len());
    let mut at = 0;
    // `body` is ASCII, so every `as u8` below keeps the character.
    while let Some(&c) = body.get(at) {
        at += 1;
        if c != '\\' {
            out.push(c as u8);
            continue;
        }
        let escaped = *body.get(at).ok_or(NotLiteral)?;
        at += 1;
        match escaped {
            '\n' => {}
            // CPython keeps the low eight bits of an octal escape above `\377`.
            '0'..='7' => out.push(octal(escaped, body, &mut at) as u8),
            'x' => out.push(hex(body, &mut at, 2)? as u8),
            other => match simple_escape(other) {
                Some(code) => out.push(code as u8),
                None => out.extend([b'\\', other as u8]),
            },
        }
    }
    Ok(out)
}

/// Python turns an int into a float exactly rounded, and refuses one that is too large.
fn int_to_float(whole: &BigInt) -> Parsed<f64> {
    whole
        .to_string()
        .parse::<f64>()
        .ok()
        .filter(|x| x.is_finite())
        .ok_or(NotLiteral)
}

struct Parser {
    chars: Vec<char>,
    at: usize,
    /// Open brackets. Inside them a newline is only whitespace.
    depth: usize,
    peeked: Option<Token>,
}

impl Parser {
    fn cur(&self) -> Option<char> {
        self.chars.get(self.at).copied()
    }

    fn look(&self, ahead: usize) -> Option<char> {
        self.chars.get(self.at + ahead).copied()
    }

    fn at_digit(&self) -> bool {
        self.cur().is_some_and(|c| c.is_ascii_digit())
    }

    fn skip_comment(&mut self) {
        while !matches!(self.cur(), None | Some('\n')) {
            self.at += 1;
        }
    }

    /// A backslash joins the next line, and something has to follow on it.
    fn join_line(&mut self) -> Parsed<()> {
        if self.look(1) != Some('\n') || self.look(2).is_none() {
            return Err(NotLiteral);
        }
        self.at += 2;
        Ok(())
    }

    /// The indentation of the line starting here, counted as CPython counts it: a tab goes to
    /// the next multiple of eight and a form feed starts over. A line joined with a backslash
    /// keeps the indentation it had before the first backslash, unless that was zero.
    fn indentation(&mut self) -> Parsed<usize> {
        let (mut column, mut joined_at) = (0, 0);
        loop {
            match self.cur() {
                Some(' ') => column += 1,
                Some('\t') => column = (column / 8 + 1) * 8,
                Some('\x0c') => column = 0,
                Some('\\') => {
                    joined_at = if joined_at == 0 { column } else { joined_at };
                    self.join_line()?;
                    continue;
                }
                _ => return Ok(if joined_at == 0 { column } else { joined_at }),
            }
            self.at += 1;
        }
    }

    /// Blank and comment lines before the expression, which must then start in column zero.
    fn leading_lines(&mut self) -> Parsed<()> {
        loop {
            let column = self.indentation()?;
            if self.cur() == Some('#') {
                self.skip_comment();
            } else if self.cur() != Some('\n') {
                return if column == 0 && self.cur().is_some() {
                    Ok(())
                } else {
                    Err(NotLiteral)
                };
            }
            if self.cur().is_none() {
                return Err(NotLiteral);
            }
            self.at += 1;
        }
    }

    /// Only blank and comment lines may follow the expression. A last line of bare whitespace
    /// with no newline counts as indented code, as it does to CPython.
    fn trailing_lines(&mut self) -> Parsed<()> {
        loop {
            let column = self.indentation()?;
            match self.cur() {
                Some('#') => self.skip_comment(),
                Some('\n') => {}
                None if column == 0 => return Ok(()),
                _ => return Err(NotLiteral),
            }
            if self.cur().is_none() {
                return Ok(());
            }
            self.at += 1;
        }
    }

    fn skip_space(&mut self) -> Parsed<()> {
        loop {
            match self.cur() {
                Some(' ' | '\t' | '\x0c') => self.at += 1,
                Some('\n') if self.depth > 0 => self.at += 1,
                Some('#') => self.skip_comment(),
                Some('\\') => self.join_line()?,
                _ => return Ok(()),
            }
        }
    }

    /// Digits with single underscores between them, as in `1_000`.
    fn decimal_digits(&mut self, out: &mut String) -> Parsed<()> {
        loop {
            while self.at_digit() {
                out.extend(self.cur());
                self.at += 1;
            }
            if self.cur() != Some('_') {
                return Ok(());
            }
            self.at += 1;
            if !self.at_digit() {
                return Err(NotLiteral);
            }
        }
    }

    /// The digits of `0x`, `0o` and `0b` literals: groups that may each start with an underscore.
    fn radix_digits(&mut self, radix: u32) -> Parsed<String> {
        let mut out = String::new();
        loop {
            if self.cur() == Some('_') {
                self.at += 1;
            }
            let before = out.len();
            while let Some(c) = self.cur().filter(|c| c.is_digit(radix)) {
                out.push(c);
                self.at += 1;
            }
            if out.len() == before {
                return Err(NotLiteral);
            }
            if self.cur() != Some('_') {
                return Ok(out);
            }
        }
    }

    fn number(&mut self) -> Parsed<PyValue> {
        let value = match (self.cur(), self.look(1)) {
            (Some('0'), Some('x' | 'X')) => self.radix_number(16)?,
            (Some('0'), Some('o' | 'O')) => self.radix_number(8)?,
            (Some('0'), Some('b' | 'B')) => self.radix_number(2)?,
            _ => self.decimal_number()?,
        };
        // Nothing that could be part of a name may touch the end of a number.
        if self.cur().is_some_and(is_name_char) {
            return Err(NotLiteral);
        }
        Ok(value)
    }

    fn radix_number(&mut self, radix: u32) -> Parsed<PyValue> {
        self.at += 2;
        let digits = self.radix_digits(radix)?;
        BigInt::from_str_radix(&digits, radix)
            .map(PyValue::Int)
            .map_err(|_| NotLiteral)
    }

    fn decimal_number(&mut self) -> Parsed<PyValue> {
        let (mut whole, mut fraction, mut exponent) = (String::new(), String::new(), String::new());
        let mut float = false;
        // `0`, `00` and `0_0` are zero; other digits after leading zeros need a `.`, `e` or `j`.
        let mut zeros_then_digits = false;
        if self.cur() == Some('.') {
            self.at += 1;
            float = true;
            self.decimal_digits(&mut fraction)?;
        } else if self.cur() == Some('0') {
            loop {
                if self.cur() == Some('_') {
                    self.at += 1;
                    if !self.at_digit() {
                        return Err(NotLiteral);
                    }
                }
                if self.cur() != Some('0') {
                    break;
                }
                whole.push('0');
                self.at += 1;
            }
            zeros_then_digits = self.at_digit();
            self.decimal_digits(&mut whole)?;
        } else {
            self.decimal_digits(&mut whole)?;
        }
        if !float && self.cur() == Some('.') {
            self.at += 1;
            float = true;
            if self.at_digit() {
                self.decimal_digits(&mut fraction)?;
            }
        }
        if matches!(self.cur(), Some('e' | 'E')) {
            self.at += 1;
            float = true;
            if let Some(sign) = self.cur().filter(|c| matches!(c, '+' | '-')) {
                exponent.push(sign);
                self.at += 1;
            }
            if !self.at_digit() {
                return Err(NotLiteral);
            }
            self.decimal_digits(&mut exponent)?;
        }
        let imaginary = matches!(self.cur(), Some('j' | 'J'));
        if imaginary {
            self.at += 1;
        }
        if !float && !imaginary {
            if zeros_then_digits {
                return Err(NotLiteral);
            }
            let digits = whole.trim_start_matches('0');
            // CPython refuses to read an int with more digits than it would print.
            return match digits.len() {
                0 => Ok(PyValue::int(0)),
                1..=MAX_INT_DIGITS => digits.parse().map(PyValue::Int).map_err(|_| NotLiteral),
                _ => Err(NotLiteral),
            };
        }
        // Spelled out in full so `1.`, `.5` and `1e5` all read the same way.
        let mantissa = format!(
            "{}.{}e{}",
            if whole.is_empty() { "0" } else { &whole },
            if fraction.is_empty() { "0" } else { &fraction },
            if exponent.is_empty() { "0" } else { &exponent },
        );
        let value: f64 = mantissa.parse().map_err(|_| NotLiteral)?;
        Ok(if imaginary {
            PyValue::Complex(0.0, value)
        } else {
            PyValue::Float(value)
        })
    }

    /// A string literal, from its opening quote. The prefix letters are already read.
    fn string(&mut self, prefix: Prefix) -> Parsed<Token> {
        let quote = self.cur().ok_or(NotLiteral)?;
        let triple = self.look(1) == Some(quote) && self.look(2) == Some(quote);
        let width = if triple { 3 } else { 1 };
        self.at += width;
        let mut body = Vec::new();
        loop {
            let c = self.cur().ok_or(NotLiteral)?;
            if c == quote
                && (!triple || (self.look(1) == Some(quote) && self.look(2) == Some(quote)))
            {
                self.at += width;
                break;
            }
            if c == '\n' && !triple {
                return Err(NotLiteral);
            }
            body.push(c);
            self.at += 1;
            if c == '\\' {
                // Whatever follows a backslash cannot end the string, raw or not.
                body.push(self.cur().ok_or(NotLiteral)?);
                self.at += 1;
            }
        }
        if prefix.format {
            // An f-string is an expression even when it has no fields.
            return Err(NotLiteral);
        }
        Ok(Token::Text(if !prefix.bytes {
            Piece::Str(if prefix.raw {
                body.iter().map(|&c| u32::from(c)).collect()
            } else {
                unescape_str(&body)?
            })
        } else if !body.iter().all(char::is_ascii) {
            return Err(NotLiteral);
        } else if prefix.raw {
            Piece::Bytes(body.iter().map(|&c| c as u8).collect())
        } else {
            Piece::Bytes(unescape_bytes(&body)?)
        }))
    }

    /// A name, or the prefix of a string literal. The only names a literal can hold are `True`,
    /// `False`, `None` and `set`.
    fn word(&mut self) -> Parsed<Token> {
        let start = self.at;
        let mut prefix = Prefix::default();
        let mut unicode = false;
        loop {
            match self.cur() {
                Some('b' | 'B') if !(prefix.bytes || unicode || prefix.format) => {
                    prefix.bytes = true
                }
                Some('u' | 'U') if !(prefix.bytes || unicode || prefix.raw || prefix.format) => {
                    unicode = true
                }
                Some('r' | 'R') if !(prefix.raw || unicode) => prefix.raw = true,
                Some('f' | 'F') if !(prefix.format || prefix.bytes || unicode) => {
                    prefix.format = true
                }
                _ => break,
            }
            self.at += 1;
            if matches!(self.cur(), Some('"' | '\'')) {
                return self.string(prefix);
            }
        }
        while self.cur().is_some_and(is_name_char) {
            self.at += 1;
        }
        let name: String = self.chars[start..self.at].iter().collect();
        match name.as_str() {
            "True" => return Ok(Token::Constant(PyValue::Bool(true))),
            "False" => return Ok(Token::Constant(PyValue::Bool(false))),
            "None" => return Ok(Token::Constant(PyValue::None)),
            "set" => return Ok(Token::SetName),
            _ if name.is_ascii() => return Err(NotLiteral),
            _ => {}
        }
        // Python compares names after NFKC, so a full-width `ｓｅｔ` is `set`. Keywords are not
        // names: a full-width `Ｔｒｕｅ` is just an unknown name.
        let mut chars = name.chars();
        let starts = chars
            .next()
            .is_some_and(|c| c == '_' || unicode_ident::is_xid_start(c));
        if starts && chars.all(unicode_ident::is_xid_continue) && name.nfkc().eq("set".chars()) {
            return Ok(Token::SetName);
        }
        Err(NotLiteral)
    }

    fn lex(&mut self) -> Parsed<Token> {
        self.skip_space()?;
        let Some(c) = self.cur() else {
            return Ok(Token::End);
        };
        match c {
            '\n' => self.at += 1,
            '0'..='9' => return self.number().map(Token::Number),
            '.' if self.look(1).is_some_and(|d| d.is_ascii_digit()) => {
                return self.number().map(Token::Number);
            }
            '.' if self.look(1) == Some('.') && self.look(2) == Some('.') => self.at += 3,
            '"' | '\'' => return self.string(Prefix::default()),
            '(' | '[' | '{' if self.depth < MAX_NESTING => {
                self.depth += 1;
                self.at += 1;
            }
            ')' | ']' | '}' => {
                self.depth = self.depth.saturating_sub(1);
                self.at += 1;
            }
            ',' | ':' | '+' | '-' => self.at += 1,
            c if c != '(' && c != '[' && c != '{' && is_name_char(c) => return self.word(),
            _ => return Err(NotLiteral),
        }
        Ok(match c {
            '\n' => Token::Newline,
            '.' => Token::Ellipsis,
            symbol => Token::Symbol(symbol),
        })
    }

    fn peek(&mut self) -> Parsed<&Token> {
        if self.peeked.is_none() {
            self.peeked = Some(self.lex()?);
        }
        self.peeked.as_ref().ok_or(NotLiteral)
    }

    fn take(&mut self) -> Parsed<Token> {
        match self.peeked.take() {
            Some(token) => Ok(token),
            None => self.lex(),
        }
    }

    /// Takes the next token if it is this symbol.
    fn eat(&mut self, symbol: char) -> Parsed<bool> {
        let found = matches!(self.peek()?, Token::Symbol(c) if *c == symbol);
        if found {
            self.peeked = None;
        }
        Ok(found)
    }

    fn expect(&mut self, symbol: char) -> Parsed<()> {
        if self.eat(symbol)? {
            Ok(())
        } else {
            Err(NotLiteral)
        }
    }

    fn eat_sign(&mut self) -> Parsed<Option<char>> {
        Ok(if self.eat('+')? {
            Some('+')
        } else if self.eat('-')? {
            Some('-')
        } else {
            None
        })
    }

    fn element(&mut self) -> Parsed<PyValue> {
        self.sum()?.value()
    }

    /// Items up to `close`, with an optional trailing comma.
    fn items(&mut self, close: char, mut each: impl FnMut(&mut Self) -> Parsed<()>) -> Parsed<()> {
        while !self.eat(close)? {
            each(self)?;
            if !self.eat(',')? {
                return self.expect(close);
            }
        }
        Ok(())
    }

    fn atom(&mut self) -> Parsed<Node> {
        Ok(Node::Value(match self.take()? {
            Token::Number(value) => return Ok(Node::Number(value)),
            Token::SetName => return Ok(Node::SetName),
            Token::Constant(value) => value,
            Token::Ellipsis => PyValue::Ellipsis,
            Token::Text(first) => self.text(first)?,
            Token::Symbol('(') => {
                if self.eat(')')? {
                    return Ok(Node::Value(PyValue::Tuple(Vec::new())));
                }
                // Brackets alone change nothing: `(1)` is still the number as written.
                let first = self.sum()?;
                if self.eat(')')? {
                    return Ok(first);
                }
                self.expect(',')?;
                let mut members = vec![first.value()?];
                self.items(')', |parser| {
                    members.push(parser.element()?);
                    Ok(())
                })?;
                PyValue::Tuple(members)
            }
            Token::Symbol('[') => {
                let mut members = Vec::new();
                self.items(']', |parser| {
                    members.push(parser.element()?);
                    Ok(())
                })?;
                PyValue::List(members)
            }
            Token::Symbol('{') => self.braces()?,
            _ => return Err(NotLiteral),
        }))
    }

    /// Adjacent string literals are one string; `str` and `bytes` do not mix.
    fn text(&mut self, first: Piece) -> Parsed<PyValue> {
        let mut whole = first;
        while matches!(self.peek()?, Token::Text(_)) {
            let Token::Text(next) = self.take()? else {
                return Err(NotLiteral);
            };
            match (&mut whole, next) {
                (Piece::Str(points), Piece::Str(more)) => points.extend(more),
                (Piece::Bytes(bytes), Piece::Bytes(more)) => bytes.extend(more),
                _ => return Err(NotLiteral),
            }
        }
        Ok(match whole {
            Piece::Bytes(bytes) => PyValue::Bytes(bytes),
            Piece::Str(points) => match points.iter().map(|&code| char::from_u32(code)).collect() {
                Some(text) => PyValue::Str(text),
                None => PyValue::Surrogates(points),
            },
        })
    }

    /// A dict or a set. A key or member that Python cannot hash makes the text not a literal.
    fn braces(&mut self) -> Parsed<PyValue> {
        if self.eat('}')? {
            return Ok(PyValue::Dict(PyDict::new()));
        }
        let first = self.element()?;
        if self.eat(':')? {
            let mut dict = PyDict::new();
            dict.set(first, self.element()?).map_err(|_| NotLiteral)?;
            if self.eat(',')? {
                self.items('}', |parser| {
                    let key = parser.element()?;
                    parser.expect(':')?;
                    dict.set(key, parser.element()?).map_err(|_| NotLiteral)
                })?;
            } else {
                self.expect('}')?;
            }
            return Ok(PyValue::Dict(dict));
        }
        let mut set = PySet::new();
        set.add(first).map_err(|_| NotLiteral)?;
        if self.eat(',')? {
            self.items('}', |parser| {
                set.add(parser.element()?).map_err(|_| NotLiteral)
            })?;
        } else {
            self.expect('}')?;
        }
        Ok(PyValue::Set(set))
    }

    fn primary(&mut self) -> Parsed<Node> {
        let atom = self.atom()?;
        if matches!(atom, Node::SetName) && self.eat('(')? {
            self.expect(')')?;
            return Ok(Node::Value(PyValue::Set(PySet::new())));
        }
        Ok(atom)
    }

    /// One sign on a number as written. `--1` and `-(-1)` are expressions, not literals.
    fn unary(&mut self) -> Parsed<Node> {
        let Some(sign) = self.eat_sign()? else {
            return self.primary();
        };
        let Node::Number(value) = self.primary()? else {
            return Err(NotLiteral);
        };
        Ok(Node::Signed(match (sign, value) {
            ('-', PyValue::Int(whole)) => PyValue::Int(-whole),
            ('-', PyValue::Float(x)) => PyValue::Float(-x),
            ('-', PyValue::Complex(re, im)) => PyValue::Complex(-re, -im),
            (_, value) => value,
        }))
    }

    /// `real + imaginary` and `real - imaginary` are the only arithmetic `literal_eval` does.
    fn sum(&mut self) -> Parsed<Node> {
        let left = self.unary()?;
        let Some(sign) = self.eat_sign()? else {
            return Ok(left);
        };
        let (Node::Number(real) | Node::Signed(real), Node::Number(PyValue::Complex(re, im))) =
            (left, self.unary()?)
        else {
            return Err(NotLiteral);
        };
        let real = match real {
            PyValue::Int(whole) => int_to_float(&whole)?,
            PyValue::Float(x) => x,
            _ => return Err(NotLiteral),
        };
        Ok(Node::Value(if sign == '+' {
            PyValue::Complex(real + re, 0.0 + im)
        } else {
            PyValue::Complex(real - re, 0.0 - im)
        }))
    }

    fn whole_text(&mut self) -> Parsed<PyValue> {
        self.leading_lines()?;
        let first = self.sum()?;
        let value = if self.eat(',')? {
            // Commas at the top level make a tuple without brackets.
            let mut members = vec![first.value()?];
            while !matches!(self.peek()?, Token::Newline | Token::End) {
                members.push(self.element()?);
                if !self.eat(',')? {
                    break;
                }
            }
            PyValue::Tuple(members)
        } else {
            first.value()?
        };
        match self.take()? {
            Token::End => Ok(value),
            Token::Newline => self.trailing_lines().map(|()| value),
            _ => Err(NotLiteral),
        }
    }
}

/// The value `ast.literal_eval(text)` returns, or `None` where it raises.
pub fn parse_literal(text: &str) -> Option<PyValue> {
    // `literal_eval` drops leading spaces and tabs; the tokenizer reads `\r\n` and `\r` as
    // newlines and refuses a NUL anywhere.
    let text = text.trim_start_matches([' ', '\t']);
    if text.contains('\0') {
        return None;
    }
    let chars = text
        .replace("\r\n", "\n")
        .replace('\r', "\n")
        .chars()
        .collect();
    let mut parser = Parser {
        chars,
        at: 0,
        depth: 0,
        peeked: None,
    };
    parser.whole_text().ok()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::repr::canon;

    /// The type and canonical text of what `text` evaluates to, or `-` where it is not a literal.
    fn eval(text: &str) -> String {
        parse_literal(text).map_or("-".into(), |value| {
            format!(
                "{} {}",
                value.type_name(),
                canon(&value).unwrap_or_default()
            )
        })
    }

    #[test]
    fn numbers() {
        // Expected values are CPython 3.11's `ast.literal_eval`.
        for (text, expected) in [
            ("1", "int 1"),
            ("-1", "int -1"),
            ("+919876543210", "int 919876543210"),
            ("1_000", "int 1000"),
            ("0x_1f", "int 31"),
            ("0o17", "int 15"),
            ("0b101", "int 5"),
            ("00", "int 0"),
            ("0_0", "int 0"),
            ("1e5", "float 100000.0"),
            ("1.", "float 1.0"),
            (".5", "float 0.5"),
            ("08.5", "float 8.5"),
            ("1e999", "float inf"),
            ("-0.0", "float -0.0"),
            ("08j", "complex 8j"),
            ("-1j", "complex (-0-1j)"),
            ("1+2j", "complex (1+2j)"),
            ("-1.5-2.5j", "complex (-1.5-2.5j)"),
            ("-0.0+0j", "complex 0j"),
            ("-(1)", "int -1"),
            ("(1)+(2j)", "complex (1+2j)"),
        ] {
            assert_eq!(eval(text), expected, "{text:?}");
        }
        for text in [
            "007", "01", "1__0", "1_", "0x", "0o8", "0b2", "1e", "1.5e", "--5", "-(-1)", "+-5",
            "5-3", "1+2", "1+2j+3j", "2j+1", "1+-2j", "-True", "1abc", "1é", "1.2.3", "inf", "nan",
            "1 2",
        ] {
            assert_eq!(eval(text), "-", "{text:?}");
        }
    }

    #[test]
    fn strings() {
        for (text, expected) in [
            ("'abc'", "str 'abc'"),
            ("\"it's\"", "str \"it's\""),
            ("'a' 'b'", "str 'ab'"),
            ("'''a\nb'''", "str 'a\\nb'"),
            ("'a\\\nb'", "str 'ab'"),
            ("r'a\\nb'", "str 'a\\\\nb'"),
            ("r'\\''", "str \"\\\\'\""),
            ("'\\x41\\u00e9\\U0001f600'", "str 'Aé😀'"),
            ("'\\1234'", "str 'S4'"),
            ("'\\400'", "str 'Ā'"),
            ("'\\8\\d'", "str '\\\\8\\\\d'"),
            ("'\\N{em dash}'", "str '—'"),
            ("'\\N{lf}\\N{NULL}'", "str '\\n\\x00'"),
            ("'\\ud83d'", "str '\\ud83d'"),
            ("b'a' b'b'", "bytes b'ab'"),
            ("b'\\400\\xff'", "bytes b'\\x00\\xff'"),
            ("rb'\\x41'", "bytes b'\\\\x41'"),
            ("b'\\N{DASH}'", "bytes b'\\\\N{DASH}'"),
        ] {
            assert_eq!(eval(text), expected, "{text:?}");
        }
        for text in [
            "'a",
            "'a\nb'",
            "r'\\'",
            "'\\x4'",
            "'\\u004'",
            "'\\U00110000'",
            "'\\N{DASH}'",
            "'\\N{EMDASH}'",
            "'\\N{SHAKING FACE}'",
            "'\\N'",
            "f'x'",
            "f''",
            "'a' b'b'",
            "b'é'",
            "ur'a'",
            "bu'a'",
            "'a'b",
            "'\0'",
        ] {
            assert_eq!(eval(text), "-", "{text:?}");
        }
    }

    #[test]
    fn containers_and_names() {
        for (text, expected) in [
            ("()", "tuple ()"),
            ("(1,)", "tuple (1,)"),
            ("1,2,3", "tuple (1, 2, 3)"),
            ("1,", "tuple (1,)"),
            ("(1)", "int 1"),
            (
                "[1, [2, (3,)], {4: None}]",
                "list [1, [2, (3,)], {4: None}]",
            ),
            ("{}", "dict {}"),
            ("{1}", "set {1}"),
            ("{1: 'a', 1.0: 'b', True: 'c'}", "dict {1: 'c'}"),
            ("{1, 1.0, True}", "set {1}"),
            ("set()", "set set()"),
            ("set (\n)", "set set()"),
            ("(set)()", "set set()"),
            ("\u{ff53}\u{ff45}\u{ff54}()", "set set()"),
            ("...", "ellipsis Ellipsis"),
            ("True", "bool True"),
            ("None", "NoneType None"),
        ] {
            assert_eq!(eval(text), expected, "{text:?}");
        }
        for text in [
            "(,)",
            "[,]",
            "[1,,2]",
            "{,}",
            "{1: 2, 3}",
            "{[1]: 2}",
            "{[1]}",
            "set(1)",
            "set",
            "true",
            "\u{ff34}\u{ff52}\u{ff55}\u{ff45}",
            "s\u{435}t()",
            "[1)",
            "[1",
            "1]",
            "x",
            "[x]",
            "{**{}}",
            "[*[1]]",
        ] {
            assert_eq!(eval(text), "-", "{text:?}");
        }
    }

    #[test]
    fn lines_and_layout() {
        for text in [
            " \t 1",
            "1\n",
            "\n\n1\n",
            "1 # c",
            "# c\n1",
            "1\n  # c",
            "\x0c1",
            "1\x0c",
            "[\n1,\n2\n]",
            "[1, # one\n2]",
            "[1\\\n,2]",
            "\\\n1",
            "\r1",
            "1\r\n",
            "[1,\r2]",
        ] {
            assert_ne!(eval(text), "-", "{text:?}");
        }
        for text in [
            "",
            " ",
            "#1",
            "\n 1",
            "1\n2",
            "1;",
            "1 \n ",
            "1\\\n",
            "\x0b1",
            "\u{feff}1",
            "1\0",
            "\u{a0}1",
        ] {
            assert_eq!(eval(text), "-", "{text:?}");
        }
    }

    #[test]
    fn limits() {
        let nested = |depth: usize| "[".repeat(depth) + &"]".repeat(depth);
        assert_ne!(eval(&nested(MAX_NESTING)), "-");
        assert_eq!(eval(&nested(MAX_NESTING + 1)), "-");
        assert_ne!(eval(&"9".repeat(MAX_INT_DIGITS)), "-");
        assert_eq!(eval(&"9".repeat(MAX_INT_DIGITS + 1)), "-");
        // Hexadecimal has no such limit when read; printing the value is what fails.
        let huge = parse_literal(&("0x".to_string() + &"f".repeat(5000)));
        assert!(huge.is_some_and(|value| canon(&value).is_err()));
        assert_eq!(eval(&"-".repeat(100_000)), "-");
    }
}
