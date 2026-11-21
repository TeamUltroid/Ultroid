# session-rs

The bridge that proves session strings in `rust/ultroid-core` against the Python original:
Ultroid's `validate_session` (`pyUltroid/startup/connections.py`) and the `StringSession` of
Telethon 1.44.0 it returns. What they do is in that crate's README.

`rust/harness/session.py` calls the original and reports what happened as data:

| Function | What it returns |
| --- | --- |
| `check(session, leave)` | what `validate_session(session, _exit=leave)` did: the session it returned (data centre, address, port, key, the string Telethon would save), that it returned nothing, that it left the program, or the exception it raised; then the messages it logged |
| `parse(text)` | what Telethon's `StringSession(text)` holds, or the exception it raises |

The messages come from `strings`, a unit of its own; a stand-in gives back the key of the
message asked for (`py_c1`, `py_c2`).

## Proof

`cases.jsonl` holds 1,382 calls recorded from the original. No real session is in them: the
strings are made the way the libraries make them, with made-up keys
(`rust/harness/session_inputs.py`, seeded).

- Telethon sessions with IPv4 and IPv6 addresses, any data centre and port, and a key of zeros.
- Pyrogram sessions in all three layouts, with data centres Ultroid knows and does not know.
- The same with blanks before or after, characters dropped, added or replaced, cut short,
  padded.
- Text that is no session, the empty string and no value at all.

Of the 848 `check` cases, 151 give a session, 410 leave the program, 132 return nothing after
logging, and 86 raise inside the original (`KeyError`, `binascii.Error`, `struct.error`,
`ValueError`). Of the 534 `parse` cases, 107 give a session.

- `rust-anything diff`: 1382/1382 match.
- `rust-anything gate`: passed.
- `rust/harness/check_shadow.py`: the recorded result comes back in `old`, `shadow` and `new`
  mode.
- `rust/harness/fuzz_session.py`: three seeded runs, 415,000 generated strings through both
  functions, no difference.

`rust-anything bench`, original against Rust with the call into Rust included (Linux x86_64,
CPython 3.11, 2026-11-20):

| Function | Python ns/call | Rust ns/call | Speedup |
| --- | ---: | ---: | ---: |
| `check` | 6501 | 4644 | 1.40x |
| `parse` | 7673 | 4349 | 1.76x |

Overall 1.57x. This runs once at start, so the speed is of no consequence.

## What is not covered

- Logging in. Whether Telegram accepts the session is out of reach here (ADR-001).
- A session that is not text. The harness takes text or nothing; the original would fail on an
  int with `AttributeError`.
- The IPv6 address is written as Python 3.11.18 writes it (`::ffff:1.2.3.4` for an IPv4 address
  in IPv6 form). Rust's standard library writes the same; other Python versions were not
  compared.

## Loop

```sh
python3 make_inputs.py > inputs.jsonl
rust-anything record . --inputs inputs.jsonl
rust-anything build . && rust-anything diff . && rust-anything gate .
```
