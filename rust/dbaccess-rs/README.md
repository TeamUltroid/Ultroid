# dbaccess-rs

The bridge that proves the database and its accessors in `rust/ultroid-db` against the Python
original: `udB`'s cache and value handling (`_BaseDatabase`), the 93 functions of
`pyUltroid/dB/*.py`, and `KeyManager`. What they do, and what the original does that one would
not guess, is in that crate's README.

These functions keep their state in the database, so they are recorded as scenarios, not as
single calls (ADR-015). `rust/harness/dbaccess.py` runs a list of steps on an empty database in
memory and reports the result of each, then the text the database holds:

```python
run([
    ["blacklist_db.add_blacklist", -1001, "spam"],
    ["$restart"],                                  # the cache is lost, the stored text stays
    ["blacklist_db.list_blacklist", -1001],
    ["$raw", "BLACKLIST_DB", "hello"],             # the stored text changed behind the cache
    ["blacklist_db.get_blacklist", -1001],
    ["$clock", 86400],                             # one day after 2000-01-01, for afk_db
])
# [["ok", "bool", "True"], ["ok", "NoneType", "None"], ["ok", "str", "'👉`spam`\\n'"],
#  ["ok", "NoneType", "None"], ["error", "AttributeError"], ["ok", "NoneType", "None"],
#  ["stored", ["BLACKLIST_DB", "hello"]]]
```

`src/port.rs` runs the same steps through `ultroid_db::call` and reports them the same way.

## Proof

`cases.jsonl` holds 949 scenarios recorded from the original, 7,968 steps in all. 749 come from
`make_inputs.py` (seeded; the generator is `rust/harness/scenarios.py`), the rest are
rust-anything's own odd inputs.

- One plain walk through each module, as the plugins use it.
- Generated scenarios that stay inside one module and a few chats, users and words, so that the
  steps meet: something is added, found, removed, read again after one of 487 restarts.
- 314 changes of the stored text behind the cache: values of another shape, text that is no
  literal, a stored time that does not parse.
- Arguments of the wrong type throughout. 1,167 steps fail, and fail the same way on both sides:
  733 `TypeError`, 143 `AttributeError`, 124 `KeyError`, 73 `ValueError`, 51 `IndexError`, 42
  `OverflowError`, 1 `UnicodeEncodeError`.

Each of the 105 names (93 accessors, 6 `KeyManager` methods, 6 of `udB`) is called at least 14
times and succeeds at least 13 times.

- `rust-anything diff`: 949/949 match.
- `rust-anything gate`: passed.
- `rust/harness/check_shadow.py`: the recorded result comes back in `old`, `shadow` and `new`
  mode.
- `rust/harness/coverage_dbaccess.py`: the recorded scenarios run 342 of the 345 lines in the
  functions of `pyUltroid/dB/*.py` and `_BaseDatabase`. The other three cannot be reached: a dead
  `except KeyError` in `forcesub_db.rem_forcesub` (two lines) and the `cache_only` branch of
  `set_key`, which nothing in Ultroid uses.
- `rust/harness/fuzz_dbaccess.py`: four seeded runs after the last fix, 1.76 million generated
  scenarios of 17.6 million steps, no difference.

`rust-anything bench`, original against Rust with the call into Rust included (Linux x86_64,
CPython 3.11, 2026-11-20):

| Function | Python ns/call | Rust ns/call | Speedup |
| --- | ---: | ---: | ---: |
| `run` (one scenario, 8.4 steps on average) | 87838 | 25432 | 3.45x |

## What the fuzzer found

The first build matched a hand-written scenario and failed the fuzzer within seconds, twice:

- `{}.pop(key)` is a `KeyError` even for a key that cannot be hashed: an empty dict answers before
  it looks at the key. With one member it is a `TypeError`. `filestore_db.del_stored(["x"])` on an
  empty store depends on it.
- `x.update({chat: {user: ...}})` looks `update` up before it builds the argument. On a stored
  list with a user that cannot be hashed, Python says `AttributeError` and the port said
  `TypeError`.

Both are in the recorded cases now, and in the unit tests of `ultroid-db`.

## What the scenarios leave out

CPython itself gives no fixed answer for these, so they cannot be recorded (ADR-015):

- A set of several members: its order follows the hash table (ADR-013). No scenario stores one,
  so an accessor working on a stored set is covered by unit tests only.
- NaN: Python finds it by identity, and the recorder hands every call the same NaN object.
- Text with a lone surrogate as an argument: it cannot cross the bridge. It does occur as
  stored text (`'\ud83d'`), which reads back as such a string.

The gate's size check compares `src/port.rs` (131 lines) with the harness (96 lines). The
accessors are in `ultroid-db`; its README has their line counts.

## Loop

```sh
python3 make_inputs.py > inputs.jsonl
rust-anything record . --inputs inputs.jsonl
rust-anything build . && rust-anything diff . && rust-anything gate .
python3 -W ignore ../harness/fuzz_dbaccess.py 1 60
```
