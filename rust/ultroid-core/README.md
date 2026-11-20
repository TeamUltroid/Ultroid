# ultroid-core

Ultroid's start-up logic in Rust: the parts of `pyUltroid/startup` and its neighbours that take
data and give data. A plain library: no Python, no Telegram, no network.

| Module | What it is | Proven in |
| --- | --- | --- |
| `session` | What a `SESSION` string is: Telethon's `StringSession`, and `validate_session` with its Pyrogram conversion | `rust/session-rs` |
| `command` | How a command is recognised: `compile_pattern`, and Python's `re.match` on the result | `rust/command-rs` |

## Session strings

```rust
use ultroid_core::session::validate_session;

let checked = validate_session(std::env::var("SESSION").ok().as_deref(), true)?;
match checked.session {
    Some(session) => { /* session.dc_id, session.server_address, session.port, session.auth_key */ }
    None => { /* checked.logged names the messages; checked.exits says whether to stop */ }
}
```

A Telethon string session is the digit `1`, then URL-safe base64 of the data centre (one byte),
its address (4 or 16 bytes), its port (two bytes) and the 256-byte key. Ultroid also accepts the
three layouts Pyrogram has used (351, 356 and 362 characters) and makes a Telethon session of
each: the data centre and the key are kept, the address becomes that data centre's IPv4
address, the port 443.

What the original does that one would not guess, all of it kept (ADR-003):

- **A line break or blank after a Telethon session crashes the start.** The length is checked on
  the stripped string and the string is then parsed with the blanks on, so the check passes and
  the parse fails with a `struct.error`. This is the usual shape of a value pasted into `.env`.
  A blank before it is the "wrong string session" message.
- **A Telethon session with an IPv6 address is refused.** Telethon reads it (369 characters);
  Ultroid's check wants 353.
- **A Telethon session of the wrong length exits even when asked not to.** `_exit=False`, which
  the voice-chat session passes, only applies to strings that are no session at all.
- **A Pyrogram session of a data centre other than 1 to 5 is a `KeyError`**, not a message.
  Every string of 351, 356 or 362 characters that does not start with `1` is taken for a
  Pyrogram session, so other text of those lengths fails with a base64 or `struct` error.
- **Pyrogram's test-server flag is dropped.** A session of a test server becomes a session of
  the production data centre with the same number.
- **A key of all zeros is no key.** The session is accepted and saves as the empty string.
- **base64 is read the way Python reads it**: characters outside the alphabet are skipped and
  nothing after complete padding is read. The decoder here is a port of that, since a strict
  decoder refuses strings Python accepts. Encoding uses the `base64` crate.

`SessionError::python_name()` gives the exception the original raises at the same point.

Proof: `rust/session-rs`, 1,382 recorded cases, gate passed.

## Commands

```rust
use ultroid_core::command::{Pattern, command_pattern};

// A plugin registered `ban( (.*)|$)`; the handler is `.`.
let ban = Pattern::new(&command_pattern("ban( (.*)|$)", "."))?;
if let Some(found) = ban.match_start(".ban @user spam") {
    // found.groups: [Some(" @user spam"), Some("@user spam")]; found.end: 15
}
```

A plugin registers a regular expression for its command. Ultroid puts the handler in front
(`command_pattern`), and Telethon matches the result against the start of every message with
`re.match`. `assistant_pattern` is the same for the assistant bot's commands; a pattern for an
inline query is used as it is.

`Pattern` reads the pattern and matches it the way Python's `re` does (ADR-017): a matcher
written after CPython's own, not a general regular expression engine, because those answer
differently in places. A `Found` is `re`'s match: where it ends, `groups()` and `groupdict()`.

What is read: characters and escapes (`\n`, `\x41`, `\u00e9`, octal), `.`, classes with ranges
and `\d \w \s`, `^ $ \A \Z \b \B`, groups (plain, `(?:...)`, `(?P<name>...)`), `|`, the repeats
`* + ? {m,n}` greedy and lazy, and references to a group by number. `Pattern::new` answers
`PatternError::Bad` where `re.compile` raises `re.error`, and `PatternError::Unsupported` for
what it does not read: flags, look-around, conditions, atomic groups, possessive repeats,
references by name, `\N{...}`, comments. Nothing is claimed for those.

What the original does that one would not guess, all of it kept (ADR-003):

- **The backslash escapes only the first character of the handler**, and what it makes of it is
  up to `re`. The handler `.` gives `\.`, a dot. A letter or digit gives an escape: with `d`
  every command answers to any digit in front (`1ping`), with `w` to any letter, digit or
  underscore, with `s` to a blank or line break; `b` is the edge of a word, so `ping` alone is
  the command and `bping` is not; `A` is the start of the text, the same; `Z` is its end, so
  no message with text in it is a command; `n`, `t`, `a` are a line break, a tab, the bell
  character; `0` is the NUL character. Any other letter (`c`, `e`) is an error in `re` for
  every command, and so is a digit from 1 to 9 or an `x`, unless the first characters of the
  command happen to complete the escape (`\x` wants two hex digits, `\1` two octal ones).
- **The rest of a longer handler is pattern.** `..` is a dot and then any character: `.xping`
  is the command, `..ping` too, `.ping` is not. With `.*` the dots are optional and `ping`
  alone is the command.
- **`$` also matches before a line break that ends the message.** `.ping` followed by one line
  break is the command `ping$`; followed by two it is not.
- **`.` stops at a line break**, so `ban ?(.*)` takes the reason up to the end of the first
  line and the rest of the message is ignored.
- **`\d`, `\w` and `\s` are Unicode.** `setflood ?(\d+)` takes `٣٤`. `\w` has letters and
  digits of every script but no combining marks; `\s` has the separators U+001C to U+001F.
  The tables are those of CPython 3.11 (Unicode 14), in `src/tables.rs`.
- **One `^` and then one `.` are dropped from the start of a plugin's pattern**, in that order
  and once each: `^.ping` and `.ping` are `ping`; `..ping` is any character and then `ping`.
- **The handler `" "` or `NO_HNDLR` means no handler**: the command stands at the start of the
  message.
- **A plugin with no pattern gets every message.**
- **`re`'s loops end after a round that took no character.** `(a|b*)*` on `abb` matches all of
  it and leaves the group empty; `(?:|a)*` on `aa` matches at once and takes neither `a`.
  `\b` and `\B` both fail in an empty text.

Like `re`, the matcher tries one way after the other. A pattern with a loop inside a loop,
such as `(a+)+b`, takes time that doubles with every `a` of a message that has no `b`. Also
like `re`, it does not start on a message that is shorter than the pattern needs. A loop that
would have to go round more than 100,000 times without taking a character is declined.

Proof: `rust/command-rs`, 9,301 recorded cases, gate passed.

## Checks

```sh
cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test
rust-anything gate ../session-rs && rust-anything gate ../command-rs
python3 ../harness/fuzz_session.py 1 60
python3 -W ignore ../harness/fuzz_command.py 1 60
```
