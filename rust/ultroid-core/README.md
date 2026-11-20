# ultroid-core

Ultroid's start-up logic in Rust: the parts of `pyUltroid/startup` and its neighbours that take
data and give data. A plain library: no Python, no Telegram, no network.

| Module | What it is | Proven in |
| --- | --- | --- |
| `session` | What a `SESSION` string is: Telethon's `StringSession`, and `validate_session` with its Pyrogram conversion | `rust/session-rs` |

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

## Checks

```sh
cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test
rust-anything gate ../session-rs
python3 ../harness/fuzz_session.py 1 60
```
