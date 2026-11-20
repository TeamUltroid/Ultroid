# Decisions

One ADR per decision the port depends on, numbered in order and never renumbered. A changed
decision gets a new ADR that supersedes the old one.

These were taken with the owner away and with an instruction not to stop for questions, so each
one is the default the facts point to, not an answer the owner gave. Status says so. Any of them
can be overturned in review; `MAP.md` lists which units each one holds back.

## ADR-001: Port only what can be proven; Python stays the running app

Status: accepted by default (2026-11-20, owner away)

Context: Ultroid is 155 Python files, 24,388 lines of code, no tests. 587 of its 878 functions
are `async`, and plugins and the assistant register 448 Telegram event handlers. What the app
does is visible only through a logged-in Telegram account. The environment this port runs in has
no Telegram account, no credentials and no database. rust-anything proves a port by replaying
behaviour recorded from the original, so behaviour that cannot be recorded cannot be proven.

Decision: A unit moves to Rust only when its behaviour can be recorded from the Python original
and replayed until `rust-anything gate` passes. Everything else stays in Python and is listed in
`MAP.md` with the exact thing that blocks it. No Rust is written for behaviour nobody can check.

Consequences: This branch does not end in a pure Rust app and `rust-anything app lift` is out of
reach. It ends in a verified foundation (the logic a Rust Ultroid must get right to stay
compatible) and a precise account of what blocks the rest.

## ADR-002: Entry points and shape

Status: accepted by default (2026-11-20, owner away)

Context: `analyze --whole-app` reports the shape as a CLI entered through
`pyUltroid/__main__.py`. In practice the entry points are `python3 -m pyUltroid` (optionally with
`API_ID API_HASH SESSION REDIS_URI REDIS_PASSWORD n` as positional arguments),
`python3 multi_client.py`, and the `startup` script that picks between them. Once started the
process is a long-running Telegram client, not a command that answers and exits.

Decision: Treat Ultroid as a CLI only for its launch path: arguments and environment, fanning out
to several clients, and the exits for missing or bad configuration. Deployment files
(`Dockerfile`, `startup`, `installer.sh`, `heroku.yml`, `app.json`, `install-termux`) are not
changed on this branch.

Consequences: Anything built in `rust/app` is opt-in. Every existing deployment keeps starting
Ultroid exactly as it does today.

## ADR-003: Equivalence bar

Status: accepted by default (2026-11-20, owner away)

Context: The ported functions return values that end up in Telegram messages and in the database.

Decision: Function level: every recorded case must match exactly, including the Python type of the
result (`3` is not `3.0`) and the exception type where the original raises. No float tolerance.
A difference is fixed in the port, never in the recording. An intended difference needs its own
ADR and a line in the crate's `known-diffs.jsonl`.

Consequences: Ports reproduce the original's quirks, including ones that look like bugs. Those are
noted in the crate's README for the owner to decide on later.

## ADR-004: Compatibility that must not change

Status: accepted by default (2026-11-20, owner away)

Context: Deployed Ultroid instances hold state the new code has to keep reading.

Decision: These stay exactly as they are: environment variable names and the positional argument
order; the `.env` file; database key names and the stored value format (values are written with
`str()` and read back with `ast.literal_eval`); the language files in `strings/strings/*.yml`;
how a command is recognised (handler prefix plus the plugin's pattern); the accepted session
string formats (Telethon, and Pyrogram converted on start).

Consequences: The database value format and the command grammar are ported and proven before
anything is built on top of them.

## ADR-005: Telegram library is undecided

Status: open (research in `research/telethon.md`)

Context: Telethon is imported by 7 of the 12 units and has no entry in rust-anything's crate
table. Every event handler, the client wrapper and the file transfer code depend on it.

Decision: None yet. No Telegram-bound unit is ported until the replacement is researched against
primary sources and there is a way to record the original against a live account (ADR-001).

Consequences: `plugins/`, `assistant/`, `assistant/manager/` and the Telegram-facing parts of
`pyUltroid/` stay in Python.

## ADR-006: Plugins and runtime code loading stay in Python

Status: accepted by default (2026-11-20, owner away)

Context: `plugins/` is 14,394 of the 24,388 lines. rust-anything marks it and `pyUltroid/fns/` as
blocked: they load and run code at runtime (plugin files installed from chat, the addons
repository, `eval` and shell commands). Rust has no equivalent of importing a `.py` file sent in
a message.

Decision: Keep the plugin system in Python on this branch. Whether a Rust Ultroid embeds Python
for plugins, replaces them with a compiled registry, or drops runtime installation is the owner's
call; the options are written up in `research/plugins.md`.

Consequences: The largest unit of the plan is out of scope until that call is made.

## ADR-007: Recording without a running bot

Status: accepted by default (2026-11-20, owner away)

Context: Most of `pyUltroid` refuses to load outside a running bot: `pyUltroid.dB` raises
`RunningAsFunctionLibError`, and `strings` reads `udB` on import. rust-anything's recorder imports
a module and calls its functions with generated and given inputs, in a temporary directory.

Decision: `rust/harness/` holds the Python needed to record: a fixture that gives the original
code an in-memory `udB` built on the original's own `_BaseDatabase`, and thin data-only functions
that call the original where its API takes or returns objects that cannot cross the bridge. The
original modules are not edited to make them recordable. Functions that touch the network, the
filesystem, a subprocess or Telegram are kept out of every recording, so the recorder never calls
them.

Consequences: `analyze` lists `rust/harness/` as a unit; it is test code, not part of the app.
A crate recorded through the harness proves the logic, not the storage engine underneath it
(Redis, MongoDB, PostgreSQL), which is not exercised here.

## ADR-008: Where Rust is wired into the running app

Status: accepted by default (2026-11-20, owner away)

Context: A shadow drop-in runs the original and the Rust port side by side. Units that hold state
(database accessors, the language cache) would split that state if only one side wrote to it.

Decision: Only stateless functions with the same signature in both languages are wired into the
Python app, and only behind a guard: when the native module is not built, the app runs the
original code path with no change in behaviour. State-holding units are ported and proven but
not wired; they are for the Rust app.

Consequences: Merging this branch changes nothing for a deployment that does not build the Rust
modules.

## ADR-009: Dependencies are chosen when a unit needs them

Status: accepted by default (2026-11-20, owner away)

Context: The plan lists 47 imported dependencies. 39 have no entry in rust-anything's crate table,
5 map to a crate only in part and 3 map well.

Decision: A crate is picked only when a unit that needs it is ported, and is then recorded
against the original like any other code. The candidates and what is known about each are in
`research/dependencies.md`. A missing crate is flagged, not quietly rewritten by hand.

Consequences: Most of the 47 stay undecided, because the units that use them are blocked.

## ADR-010: Targets

Status: accepted by default (2026-11-20, owner away)

Context: Ultroid is deployed on Linux servers and containers, Heroku-style platforms and Termux
on Android.

Decision: Crates are built and gated on Linux x86_64 with Rust 1.97 and bridged to CPython 3.9+
through PyO3's stable ABI. Nothing is built for Termux/Android here.

Consequences: Whether the Rust modules build on Termux is unknown and listed as an open question.

## ADR-011: Checkpoints and cutover

Status: accepted by default (2026-11-20, owner away)

Context: The owner asked not to be stopped for approval and to review through a draft pull
request.

Decision: No blocking checkpoints. Each unit is its own commit with its gate result, pushed as it
passes. There is no cutover on this branch: Ultroid keeps starting with `python3 -m pyUltroid`.

Consequences: The pull request is the review surface; `MAP.md` and `HANDOFF.md` say where the
port stands at any commit.
