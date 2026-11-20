# Handoff

Where the port stands at this commit, how to check it, and what comes next. `MAP.md` has every
unit; this file is for whoever picks the work up, maintainer or agent.

## In one paragraph

Ultroid still runs as it did: nothing outside `rust/` has changed (ADR-012). Under `rust/` are
two plain Rust libraries with the logic that could be proven without a Telegram account
(`ultroid-db`, `ultroid-core`), eight bridge crates that hold that logic against the Python
original case by case, a launcher binary (`app/`), and the harness used to record and fuzz. What
is not here is everything that talks to Telegram, which is most of Ultroid, and it is not here
because there was nothing to record it against.

## What is proven

A unit is listed only if `rust-anything gate` passes for it. "Fuzzed" is a differential run
against the Python original with generated inputs, on top of the recorded cases.

| What | Rust | Proof | Recorded | Fuzzed, no difference |
| --- | --- | --- | ---: | ---: |
| `time_formatter`, `humanbytes`, `numerize` | `helper-rs` | itself | 213 | |
| `get_msg_button`, `text_set`, `stdr`, `cmd_regex_replace`, `get_chat_and_msgid` | `tools-rs` | itself | 809 | |
| What `set_key` stores and `get_key` reads back | `ultroid-db` | `dbvalue-rs` | 4,394 | 13.3 million values |
| The 93 accessors of `pyUltroid/dB`, `KeyManager`, `udB`'s cache | `ultroid-db` | `dbaccess-rs` | 949 scenarios | 17.6 million steps |
| `validate_session`, Telethon's `StringSession` | `ultroid-core::session` | `session-rs` | 1,382 | 415,000 strings |
| `compile_pattern` and `re.match` on the result | `ultroid-core::command` | `command-rs` | 9,301 | 1.5 million cases |
| Which clients `multi_client.py` starts | `ultroid-core::launch` | `launch-rs` | 1,714 | 191,287 environments |
| `get_string`, `get_help`, `get_languages` | `ultroid-core::strings` | `strings-rs` | 1,716 scenarios | 105,599 scenarios |
| `multi_client.py` as a program | `app` | `app-cases` | 13 runs | |

20,478 recorded cases in the bridge crates. Each crate's README says what its cases are, what
they leave out, and what the benchmark measured.

## How to check it

Needs Rust 1.97, `rust-anything` 2.1.0 (`cargo install rust-anything`), and a Python with
Ultroid's requirements (recorded under CPython 3.11.18 with Telethon 1.44.0). PyYAML is needed
only for `compare_readers.py`.

```sh
cd rust
for lib in ultroid-db ultroid-core app; do (cd $lib && cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test); done
for crate in helper-rs tools-rs dbvalue-rs dbaccess-rs session-rs command-rs launch-rs strings-rs; do
  rust-anything build $crate && rust-anything gate $crate
done
rust-anything app replay .. --build app/target/debug/multi_client
rust-anything map .. --write          # PORT_MAP.md: says when an original changed since it was recorded
```

The fuzzers are in `harness/` (`fuzz_*.py`, each with its usage on top); they need the crate
they compare built first. `python3 -W ignore harness/command_versions.py` under another Python
says whether its `re` still answers the recorded command cases the same (3.11, 3.12 and 3.13
do).

## What is open, and why

| What | State |
| --- | --- |
| Reading a language file | Open on a decision (ADR-018). Ultroid has two readers that disagree on 138 keys; see `research/language-files.md`. |
| `json_parser` (`pyUltroid/fns/tools.py`) | Open. It is Python's `json.loads` and `json.dumps` with a fall back to `ast.literal_eval`; the literal reader is in `ultroid-db`, the `json` module is not ported. |
| Database backends (Redis, MongoDB, PostgreSQL, local file) | Blocked: there was no server to record against. `ultroid-db` has the `Store` trait they go behind and one store in memory. `research/dependencies-core.md` lists the traps. |
| `callback(...)` patterns | Not started. They are matched against bytes, where `\w`, `\d`, `\s` are ASCII; the matcher in `ultroid-core::command` reads text. |
| Who may use a command, which handler is in force | Not started: small, reads the database (`HNDLR`, `SUDO_HNDLR`, sudo users), but is tied to events. |
| `plugins/`, `assistant/`, the client, the loaders | Blocked on ADR-005, ADR-006 and an account to record against. 448 handlers. |

## What the maintainers are asked

Nothing done so far waits on these; everything Telegram-bound does.

1. **Which Telegram library** a Rust Ultroid is built on (ADR-005, `research/telethon.md`).
2. **What happens to plugins** installed at run time and to the addons repository (ADR-006,
   `research/plugins.md`).
3. **A test account** whose behaviour may be recorded.
4. **Which reader of the language files is meant** (ADR-018). Adding `pyyaml` to
   `requirements.txt` would settle it for the Python side without any of this port.
5. Whether the Rust modules must build on Termux (ADR-010).

## What was found in the Python code

Kept as it is in the port (ADR-003) and written down where the unit is described:
`ultroid-db/README.md` (stored values and accessors), `ultroid-core/README.md` (sessions,
commands, the launcher, language strings), `research/language-files.md`. The ones most likely
to matter to a user of Ultroid today:

- With a language other than English, a string that language lacks reads `Warning: could not
  load any string ...` until the language menu has been opened once, because English is not
  loaded before.
- Without PyYAML, 138 strings in 15 languages are cut off or mangled, and every value of a
  language file is passed to `eval`.
- On a machine that sets `LANGUAGE` for its own programs, every string is sent to Google
  Translate the first time it is used.
- A line break after the `SESSION` value crashes the start with a `struct.error`.
- `multi_client.py` puts the session and the Redis password on the command line of each client.
- A phone number stored as `"+91..."` comes back as a number without the plus.

## Notes for whoever continues

- The decisions are in `DECISIONS.md` (ADR-001 to 019). All were taken without the owner and
  say so. Read ADR-001, 003, 007, 012, 014 and 017 first.
- A passing gate proves the recorded cases, not the function. Three ports here passed their
  recorded cases while being wrong, and a fuzzer found each. Write the fuzzer with the unit.
- Recording goes through `harness/`, because the original modules refuse to load outside a
  running bot (ADR-007). A harness file must not contain `raise`: the gate asks for a recorded
  failing case for each, so let Python fail naturally instead (`"" + value`).
- `rust-anything bridge` needs `--force` for a harness file, and writes an absolute `root`
  into the crate's `rust-anything.json`; set it to `"../.."` before committing.
- The bridge can only raise Python's built-in exceptions. Where the original raises another
  (`struct.error`, `re.error`), the harness reports it as data.
- Shadow drop-ins hold absolute paths and are not committed; `harness/check_shadow.py` checks a
  freshly generated one in all three modes.
- The repository's `.gitignore` ignores `test*`. `rust/.gitignore` takes `app/tests/` back out;
  anything else named that way under `rust/` needs the same.
- `app/` is not lifted on purpose (ADR-019): `rust-anything app lift` would take the bindings
  out of `launch-rs`, and its cases are checked through them.
