# dbvalue-rs

The bridge that proves the database value format in `rust/ultroid-db` against the Python
original. The format itself is described in that crate's README.

The original has no function for "read stored text" or "store a value": both live inside
`_BaseDatabase.get_key` and `set_key` in `pyUltroid/startup/_database.py`, which cannot be imported
outside a running bot. `rust/harness/dbvalue.py` drives that class over a dict (ADR-007) and
exposes the two directions:

| Function | What it returns |
| --- | --- |
| `read_stored(text)` | the type and `repr` of what `get_key` returns for a key stored as `text` |
| `write_value(value)` | the type and `repr` of what `set_key` keeps, and the text it stores |

## Proof

`cases.jsonl` holds 4,394 calls recorded from the original. `inputs.jsonl` is built by
`make_inputs.py` (seeded, rerun to regenerate):

- `str()` and `repr()` of 657 nested values in the shapes the accessors store, with quotes,
  escapes, emoji, control characters, big ints and special floats;
- setting values as people type them: handler characters, phone numbers, tokens, `True`, `007`;
- Python literal syntax at its edges: every number form, string prefix and escape, comments,
  line joining, 200 levels of nesting, 4,300-digit ints;
- random edits of all of the above, to find the near misses.

968 of the 3,274 stored texts read as literals; the rest must stay text, and do.

- `rust-anything diff`: 4394/4394 match.
- `rust-anything gate`: passed.
- `rust/harness/check_shadow.py`: the recorded result comes back in `old`, `shadow` and `new`
  mode.
- `rust/harness/fuzz_dbvalue.py`: six seeded runs after the last fix, 11.4 million generated
  inputs, no difference.

`rust-anything bench`, original against Rust with the call into Rust included (Linux x86_64,
CPython 3.11, 2026-11-20):

| Function | Python ns/call | Rust ns/call | Speedup |
| --- | ---: | ---: | ---: |
| `read_stored` | 12235 | 2084 | 5.87x |
| `write_value` | 7466 | 3489 | 2.14x |

Overall 3.54x: `ast.literal_eval` compiles its argument, and Ultroid calls it on every key it
loads. This is the first unit where Rust is faster through the bridge.

## What the recording does not compare

Where a value holds a set with more than one member, both sides print the set with its members
sorted before comparing (`has_set_order` in the harness and in `src/port.rs`). CPython's own
order follows its hash table and changes between runs for text, so it cannot be recorded
(ADR-013).

The gate's size check compares `src/port.rs` (71 lines) with the harness (19 lines). The work is
in `ultroid-db`, which replaces `ast.literal_eval` and `repr`: C code in CPython, with no Python
lines to hold it against.

## Loop

```sh
python3 make_inputs.py > inputs.jsonl
rust-anything record . --inputs inputs.jsonl
rust-anything build . && rust-anything diff . && rust-anything gate .
```
