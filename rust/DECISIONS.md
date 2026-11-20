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

Status: superseded by ADR-012

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
`research/dependencies-core.md` and `research/dependencies-plugins.md`. A missing crate is
flagged, not quietly rewritten by hand.

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

## ADR-012: The Python app is not modified on this branch

Status: accepted by default (2026-11-20, owner away); supersedes ADR-008

Context: The first ported unit (`helper-rs`) measured 1.04x against the original with the call
into Rust included, so wiring it into the app buys nothing today. rust-anything's shadow drop-in
for Python holds absolute paths to the checkout it was generated in, and nothing in the
deployment builds the native modules. Wiring would mean editing `pyUltroid` for no gain, with
only the owner able to try it against Telegram.

Decision: Nothing outside `rust/` changes on this branch. Each unit's shadow drop-in is generated
per checkout (`rust-anything shadow <crate>`, not committed) and checked in `old`, `shadow` and
`new` mode by `rust/harness/check_shadow.py`. Importing a shadow in place of an original module
is left as a one-line change for the owner to make when a unit is worth switching.

Consequences: The pull request is purely additive and cannot change how Ultroid behaves. The
ported units are proven but not in use.

## ADR-013: The order a set prints in is not part of the stored format

Status: accepted by default (2026-11-20, owner away)

Context: `set_key` stores `str(value)`. For a set, CPython lists the members in the order of its
hash table. For text members that order depends on the hash seed the process started with, so the
same bot writes the same set differently after a restart. Nothing in `pyUltroid/` stores a set
today; one gets in when a user stores text that reads as one (`{1, 2}`) or a plugin passes one.

Decision: The Rust side keeps and prints set members in insertion order. Recorded cases with a
set of more than one member compare with the members sorted on both sides, in the harness and in
the port.

Consequences: The stored text of a set can differ between Python and Rust, and between two runs
of Python. Either side reads the other's text back as the same set, so no data is lost. Code that
depends on the order a stored set comes back in was already unreliable.

## ADR-014: The database layer is a library, proven through thin bridge crates

Status: accepted by default (2026-11-20, owner away)

Context: rust-anything bridges one unit to one crate and checks the port's size against the
unit's Python lines. The database layer does not fit that shape. `pyUltroid/dB/` cannot be
bridged as a directory (ten of its modules define `get_stuff`), its modules refuse to load outside
a running bot (ADR-007), and the value format underneath them is fifteen lines of Python
(`_get_data` and `set_key`) resting on `ast.literal_eval` and `str()`, which are C code inside
CPython. A Rust Ultroid also needs this layer as ordinary Rust, with no Python in the build.

Decision: `rust/ultroid-db` is a plain library crate with no bridge. Each part of it is proven by
a bridge crate whose `port.rs` only converts arguments and calls the library, recorded against a
harness module that does the same for the original (`dbvalue-rs` over `harness/dbvalue.py`).

Consequences: The gate's size check measures only the thin layer, so it says nothing about the
library. The library's README carries the real line counts, and says where the Rust has no
Python lines to be compared with. `ultroid-db` is the first crate a Rust app can depend on
directly.

## ADR-015: The accessors are proven as scenarios

Status: accepted by default (2026-11-20, owner away)

Context: The 93 functions of `pyUltroid/dB` and `KeyManager` keep their state in the database.
One call says little about them: what matters is what a later call sees, and what a restart
leaves, since the cache holds live objects and the store holds their text. Two of the functions
read the clock. rust-anything records one call of one function at a time.

Decision: The recorded unit is `rust/harness/dbaccess.py`, whose one function runs a scenario: a
list of steps on an empty database in memory, each step a call by name, a restart, a change of
the stored text behind the cache, or a new time. It reports the type and `repr` of every
result, the exception type of every failure, and the stored text at the end. The Rust side runs
the same steps through `ultroid_db::call`. The clock is handed to the AFK functions, in the
harness by replacing `datetime` in `afk_db`. `rust/harness/scenarios.py` generates the scenarios,
`fuzz_dbaccess.py` keeps generating new ones, and `coverage_dbaccess.py` checks that the recorded
ones run every reachable line of the original.

Left out, because CPython itself gives no fixed answer: a set of several members (ADR-013), NaN
(found by identity) and text with a lone surrogate as an argument (it cannot cross the bridge).
Narrowed, because nothing in Ultroid uses more: database keys are text, `KeyManager` casts are
`None` and `list`, and `set_key(cache_only=True)` is not ported.

Consequences: Only the in-memory store is exercised. Redis, MongoDB, PostgreSQL and the local
file are behind the `Store` trait and not ported; what each returns for a write, and how each
fails, is not recorded (`research/dependencies-core.md` lists what is known). A function is
proven together with the functions around it, so a recorded scenario that fails names a step,
not a function.

## ADR-016: Start-up logic is a second library, `ultroid-core`

Status: accepted by default (2026-11-20, owner away)

Context: After the database, the logic that can be proven offline is spread over the start-up
path: what a session string is, how a command is recognised, which clients to start. None of it
belongs in the database crate, and each piece is too small to be a crate of its own.

Decision: It goes into `rust/ultroid-core`, a plain library like `ultroid-db` (ADR-014), one
module per piece, each proven by its own bridge crate over a harness module. Where the original
raises an exception that is no built-in (`struct.error`, `binascii.Error`), the harness reports
the outcome as data, because the bridge can only raise built-in exceptions.

Consequences: `ultroid-core` and `ultroid-db` are what a Rust application would be built from.
Neither has Telegram, a network or Python in it.

## ADR-017: Command patterns are matched by a matcher of our own that follows `re`

Status: accepted by default (2026-11-20, owner away)

Context: A command pattern is a regular expression written for Python's `re`. The first port
translated it for a Rust engine (`fancy-regex` 0.20.2, which hands plain patterns to `regex`).
All 8,895 recorded cases matched. A differential fuzz then found ten wrong answers, from three
causes:

- `fancy-regex` rewrites patterns before it runs them. It turns `(X+)*` into `(X+)?` without
  looking whether the inner repeat is lazy, and puts a lazy repeat between two greedy ones into
  a greedy group (`optimize.rs`: `optimize_nested_repeats`, `build_concat_repeat_triplet`). So
  `(a+?)*` on `aaaa` matched one `a`, where Python and `regex` match four.
- A loop whose body can match nothing. `re` ends a loop after a round that took no character;
  `regex` goes on to the body's other alternatives. `(?:|a)*` on `aa` is the empty match in
  Python and `aa` in `regex`.
- `\b` and `\B` both fail in an empty text in Python 3.11. The translation said `\B` holds
  there.

The first can be avoided only by knowing every rewrite of one version of one crate, the second
is how the two engines are defined.

Decision: `ultroid-core` reads the pattern and matches it itself. The matcher follows
`SRE(match)` in CPython 3.11.18 (`Modules/_sre/sre_lib.h`): it tries one way after the other,
and its loops have `re`'s rules. No regular expression crate is used.

Consequences:

- The answer is Python's by construction, and by proof: recorded cases, and a fuzz that now
  compares lazy loops, loops over nothing, counts and references to groups as well.
- Fewer patterns are declined: 100 of 8,600 generated inputs. With the translation it was 490
  of 8,584, from a generator that did not yet write counts or references.
- Like `re`, the matcher can take time that doubles with every character on a pattern with
  loops inside loops. The Rust engines cannot. A caller that must not wait will need a limit
  on steps; nothing needs one yet. What `re` does to avoid the work is done here too: a text
  shorter than the pattern needs is not tried.
- A loop that would go round more than 100,000 times without taking a character
  (`(a?){100001}`) is declined. `re` accepts it and then uses memory for every round.
- Not read: flags, look-around, conditions, atomic groups and possessive repeats, references
  by name, `\N{...}`, comments. None of the 329 registered patterns uses one.
