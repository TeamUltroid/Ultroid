# Ultroid to Rust: the map

This file carries the port between sessions: the goal, the decisions, every unit with its state,
and what is out of scope. It is the plan and the claims. The measured state (functions in Rust,
cases, last diff) is generated into `PORT_MAP.md` by `rust-anything map --write`.

- `PLAN.md`: rust-anything's own plan (`analyze --whole-app`), unedited.
- `DECISIONS.md`: the decisions (ADRs). Taken by default with the owner away; all open to review.
- `GLOSSARY.md`: Ultroid's terms and their names in Rust.
- `harness/`: the Python used to record the original (ADR-007) and to check the shadow
  drop-ins (ADR-012).
- `research/`: what is known about each dependency, with sources.

## Goal

Move Ultroid to Rust one verified piece at a time. A piece counts as ported only when
`rust-anything gate` passes against behaviour recorded from the Python original.

## What can and cannot be done here

Ultroid is a Telegram client. Almost all of it is event handlers whose behaviour is visible only
through a logged-in account, and there is no account, credential or database in the environment
this port runs in. So the port is split in two (ADR-001):

- **Provable now**: logic that takes data and returns data. It is recorded from the original
  (directly, or through `harness/` where the original refuses to load outside a running bot)
  and ported until the gate passes.
- **Blocked**: everything that talks to Telegram, the network or a subprocess, and the plugin
  system. It stays in Python until the decisions and the recording it needs exist.

## Decisions

| ADR | Decision | Status |
| --- | --- | --- |
| 001 | Port only what can be proven; Python stays the running app | default |
| 002 | Entry points and shape; deployment files untouched | default |
| 003 | Equivalence bar: exact match, types included | default |
| 004 | Compatibility that must not change (env, DB format, strings, commands, sessions) | default |
| 005 | Telegram library | **open** |
| 006 | Plugins and runtime code loading stay in Python | default |
| 007 | Recording without a running bot (`harness/`) | default |
| 008 | Where Rust is wired into the running app | superseded by 012 |
| 009 | Dependencies are chosen when a unit needs them | default |
| 010 | Targets: Linux x86_64, Rust 1.97, CPython 3.9+ | default |
| 011 | No blocking checkpoints; no cutover on this branch | default |
| 012 | The Python app is not modified on this branch | default |

"default" means taken without the owner, from the facts; see `DECISIONS.md`.

## Units

States: `open`, `claimed by <session> <date>`, `done` (with gate result), `blocked` (with what
unblocks it), `keep` (stays in Python by decision).

### Provable now

Parts of the plan's tangled wave-0 piece (`pyUltroid/`, `pyUltroid/_misc/`, `pyUltroid/dB/`,
`pyUltroid/fns/`, `pyUltroid/startup/`, `strings/`), taken file by file because the directory
units cannot be bridged whole (`pyUltroid/fns/` defines `download_file` twice and is blocked on
dynamic code).

| Unit | What is ported | Recorded | State |
| --- | --- | --- | --- |
| `pyUltroid/fns/helper.py` | `time_formatter`, `humanbytes`, `numerize` | directly | done: `helper-rs`, gate passed, 213/213 cases |
| `pyUltroid/fns/tools.py` | `get_msg_button`, `text_set`, `stdr`, `cmd_regex_replace`, `get_chat_and_msgid` | directly | done: `tools-rs`, gate passed, 789/789 cases; 0.83x across the bridge, so not for use from Python |
| `pyUltroid/fns/tools.py` | `json_parser` | directly | open: needs the Python literal parser from the database value format |
| database value format (`pyUltroid/startup/_database.py`) | what `set_key` stores and `get_key` reads back | harness | open |
| `pyUltroid/dB/` | the 93 accessor functions, over an in-memory store | harness | open |
| `strings/` | language file loading and `get_string` lookup with English fallback | harness | open |
| command patterns (`pyUltroid/_misc/_decorators.py`) | `compile_pattern`, checked on every pattern the plugins register | harness | open |
| session strings (`pyUltroid/startup/connections.py`) | Telethon check and Pyrogram conversion in `validate_session` | harness | open |
| `multi_client.py` | which clients to start, from the environment | app cases | open |

### Blocked

| Unit | Lines | Blocked on |
| --- | ---: | --- |
| `plugins/` | 14,394 | ADR-005, ADR-006, and recording against a live account |
| `assistant/` | 2,821 | ADR-005 and recording against a live account |
| `assistant/manager/` | 495 | ADR-005 and recording against a live account |
| rest of the core (`pyUltroid/`: client, decorators, loaders, startup, Telegram-facing functions) | most of 6,171 | ADR-005 and recording against a live account |

### Keep

| Unit | Lines | Why |
| --- | ---: | --- |
| `resources/startup/` | 331 | Interactive installers: they prompt on stdin and run `pip` and `apt`. |
| `resources/session/` | 152 | Interactive session generator: it logs in to Telegram. |

## Open questions for the owner

1. ADR-005: which Telegram library a Rust Ultroid is built on.
2. ADR-006: what happens to runtime-installed plugins and the addons repository.
3. A Telegram test account whose behaviour may be recorded, so the blocked units can be proven.
4. ADR-010: whether the Rust modules must build on Termux.

## Out of scope on this branch

Deployment changes, a cutover, and any Rust for behaviour that cannot be recorded.
