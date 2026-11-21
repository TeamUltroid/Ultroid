# ultroid-db

Ultroid's database layer in Rust. A plain library: no Python, no bridge.

Ultroid keeps all of its state in one key-value database: Redis, MongoDB, PostgreSQL or a local
file. Whatever the backend, `set_key` stores the text of Python's `str(value)` and `get_key` reads
it back with `ast.literal_eval`, keeping the text when that fails. A Rust Ultroid has to read and
write exactly that text, or every existing deployment loses its data (ADR-004).

| Module | What it is | Lines |
| --- | --- | ---: |
| `value` | Python values, with Python's rules for equal keys, truth and type names | 222 |
| `literal` | `ast.literal_eval`: Python's tokenizer rules and the expressions it allows | 729 |
| `repr` | `repr()` and `str()`, character for character | 195 |
| `database` | `udB`: the cache and value handling of `_BaseDatabase`, over any store of text | 159 |
| `ops` | What `in`, `[]`, `int()`, `.get()`, `.pop()`, `.split()` and the like do to a value, and how each fails | 341 |
| `clock` | The `strftime`, `strptime` and time difference `afk_db` uses | 222 |
| `access` | The 93 functions of `pyUltroid/dB` and `KeyManager`, under their Python names | 836 |
| `call` | The same by name, for a bridge or a test | 166 |
| `bridge` | The JSON the test bridge carries values in; only used to prove the rest | 131 |
| `tables` | Unicode tables of the recording interpreter, generated | 1,904 |

Lines are code without tests, blanks and comments. `access`, `database` and `call` are 1,161
lines for 490 lines of Python (`pyUltroid/dB/*.py` and `_BaseDatabase`). `literal`, `repr`, `ops`
and `clock` stand in for C code inside CPython, which has no Python lines to be held against.

```rust
use ultroid_db::access::notes_db;
use ultroid_db::{Database, MemoryStore, PyValue};

let mut db = Database::new(MemoryStore::new());
let (chat, word) = (PyValue::int(-1001234567890_i64), PyValue::str("rules"));
let (msg, none) = (PyValue::str("be kind"), PyValue::None);
notes_db::add_note(&mut db, &chat, &word, &msg, &none, &none)?;
notes_db::get_notes(&mut db, &chat, &word)?; // {'msg': 'be kind', 'media': None, 'button': None}
```

A backend is anything that implements `Store` (four methods over text). Only `MemoryStore` exists
so far; Redis, MongoDB, PostgreSQL and the local file are not ported.

## What the format does

Worth knowing before touching anything that stores a setting:

- Text that reads as a Python literal is kept as that literal. Storing `"+919876543210"` keeps
  the int `919876543210` and the plus sign is gone. `"1,2,3"` becomes a tuple, `"5 # note"`
  becomes `5`, `"True"` a bool, `"0x10"` the int `16`, `"1e5"` the float `100000.0`, `"..."` the
  `Ellipsis` object.
- Text that does not read as a literal stays text: `"007"`, `"true"`, a bot token, a session
  string.
- What is stored is `str()` of the kept value, so `"1e5"` is written back as `100000.0` and
  `"'abc'"` as `abc`.
- A value whose `repr` is not a literal does not survive a restart as itself: `[inf]` comes back
  as the text `"[inf]"`. After `set_flood(chat, float("inf"))` and a restart, every antiflood
  function fails, because the whole key is now text.
- Dict keys follow Python: `1`, `1.0` and `True` are one key.
- `rename` writes the value through `set_key` again, so a key stored as `'5'` (text) arrives as
  the int `5`.
- A key that was missing when first read stays `None` until a restart or `re_cache()`, whatever
  another process has written since.

## What the accessors do that one would not guess

All of it is the original's behaviour, kept and recorded. None of it is fixed here (ADR-003).

- `asstcmd_db.cmd_reply` gives back the button only while a command named `button` exists: it
  asks the table of commands, not the command, whether there is one.
- `notes_db.list_note` finds the chat by `int(chat)` and then lists `stored[chat]` as given, so a
  chat passed as text (`"-100123"`) is a `KeyError` where `get_notes` works.
- `blacklist_db.add_blacklist` stores the first word of a chat whole (`"spam eggs"` is one
  entry) and splits every later one on blanks.
- `gban_mute_db.gmute` and `vc_sudos.add_vcsudo` add without looking: twice is two entries, and
  removing takes one away.
- `gban_mute_db.ungmute` and `echo_db.rem_echo` look for the user as given and then remove
  `int(user)`. A user passed as text is never found, although `gmute("111")` did add `111`.
- `mute_db.unmute` and `echo_db.rem_echo` write the key on every call, changed or not.
- `warn_db.add_warn` catches everything: if the chat's entry cannot take the warning for any
  reason, the entry is replaced by this one warning. `warns` answers `(0, None)` to anything it
  cannot read, and `reset_warn` also swallows a failed save.
- `filestore_db.del_stored` is a `KeyError` for a hash that is not stored.
- `botchat_db` keeps message ids and the name `TAG` in one dict, so `add_stuff("TAG", x)` breaks
  every tag.
- Not found is `None`, `False`, `(False, False)`, `(0, None)` or `''`, depending on the function.
  `echo_db.check_echo` answers `True` or `None`.
- `forcesub_db.rem_forcesub` has an `except KeyError: return False` that cannot be reached.
- `KeyManager.add` says nothing when it does nothing: an item for a stored value that is neither
  list nor dict is dropped. With `cast=list`, a stored value that is no list is treated as a list
  of that one value.
- `afk_db.is_afk` raises when the stored time does not parse, and reports a negative time
  (`-1 day, 23:59:55`) when the clock went back.

## Proof

- The format: `rust/dbvalue-rs`, 4,394 recorded cases, gate passed, and
  `rust/harness/fuzz_dbvalue.py`.
- The database and the accessors: `rust/dbaccess-rs`, 949 recorded scenarios of 7,968 steps, gate
  passed, and `rust/harness/fuzz_dbaccess.py`. The scenarios run every reachable line of the
  original's functions (`rust/harness/coverage_dbaccess.py`).

Both fuzzers found differences the recorded cases had missed; each is fixed, recorded, and
described in the bridge crate's README.

## Where it differs from the original

- **Results are copies.** `get_stuff()` and its like hand out the cached object in Python, and a
  caller that changes it changes the cache. Here the caller gets a value of its own.
- **Keys are text.** `get_key(5)` works in Python: it reads the key `"5"` and remembers it under
  `5`. Only text keys are ported.
- **`KeyManager` casts.** `None` and `list`, which is all the code base passes.
- **`set_key(..., cache_only=True)`** is not ported: nothing in Ultroid passes it.
- **`asstcmd_db.list_cmds`** gives a list of the names, not a view of the dict's keys.
- **What a write answers.** The accessors return what the backend's `set` returns. `call`
  reports `True`, as the in-memory database of the harness does; the real backends were not run.
- **The clock** is an argument of the two AFK functions that need it. Reading the local time is
  left to the application. A year before 1000 is written without leading zeros, as glibc writes
  it.
- **Set order.** CPython prints a set in the order of its hash table, which for text members
  changes from run to run. This crate prints members in insertion order. Each side reads what
  the other writes (ADR-013).
- **Unicode version.** `repr()` escapes what `str.isprintable()` rejects, `\N{...}` knows only
  the interpreter's characters, and `int()` and `split()` go by its digits and blanks. All are
  tied to the Unicode version CPython was built with, so `tables.rs` is generated from the
  recording interpreter (CPython 3.11.18, Unicode 14.0) by `rust/harness/gen_tables.py`. A
  deployment on another Python prints newer characters differently; both forms read back the
  same. The check that makes a full-width `ｓｅｔ()` an empty set uses the `unicode-ident` crate,
  which follows a newer Unicode.
- **NaN.** Python finds a NaN in a list or as a dict key by object identity. Values here have no
  identity, so a NaN is never found.
- **Lone surrogates.** Text like `'\ud83d'` reads as a `str` Python can hold but no backend can
  store. It is kept as code points (`PyValue::Surrogates`); storing it is the
  `UnicodeEncodeError` the Python drivers raise, and the cache keeps it all the same.
- **Int size.** CPython refuses to print or read an int of more than 4,300 digits unless told
  otherwise (`sys.set_int_max_str_digits`). The limit here is fixed at 4,300.
- **Python version.** The rules are those of CPython 3.11, the recording interpreter. Python 3.9,
  which ADR-010 still allows, does not strip leading spaces and tabs before reading a literal
  (`ast.literal_eval` does since 3.10), so text stored as ` 5` is the int `5` here and on 3.10 and
  later, and stays text on 3.9. The digit limit above came with 3.11 and with the security
  releases of the older versions.

Not proven by recorded cases, only by unit tests: an accessor working on a stored set (for
example after `.setdb GMUTE {111}`). A set of several members has no order to record.

## Checks

```sh
cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test
rust-anything gate ../dbvalue-rs && rust-anything gate ../dbaccess-rs
python3 -W ignore ../harness/fuzz_dbvalue.py 1 60
python3 -W ignore ../harness/fuzz_dbaccess.py 1 60
python3 -W ignore ../harness/coverage_dbaccess.py
```
