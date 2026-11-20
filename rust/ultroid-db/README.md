# ultroid-db

Ultroid's database layer in Rust. A plain library: no Python, no bridge.

Ultroid keeps all of its state in one key-value database: Redis, MongoDB, PostgreSQL or a local
file. Whatever the backend, `set_key` stores the text of Python's `str(value)` and `get_key` reads
it back with `ast.literal_eval`, keeping the text when that fails. A Rust Ultroid has to read and
write exactly that text, or every existing deployment loses its data (ADR-004). So far this crate
is that format:

| Module | What it is | Lines |
| --- | --- | ---: |
| `value` | Python values, with Python's rules for equal keys, truth and type names | 219 |
| `literal` | `ast.literal_eval`: Python's tokenizer rules and the expressions it allows | 729 |
| `repr` | `repr()` and `str()`, character for character | 187 |
| `bridge` | The JSON the test bridge carries values in; only used to prove the rest | 131 |
| `tables` | Unicode tables of the recording interpreter, generated | 1,886 |

Lines are code without tests, blanks and comments.

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
  as the text `"[inf]"`.
- Dict keys follow Python: `1`, `1.0` and `True` are one key.

## Proof

`rust/dbvalue-rs` bridges two functions to the Python original and replays 4,394 recorded cases:
4394/4394 match, gate passed. `rust/harness/fuzz_dbvalue.py` runs both sides on generated text
and values; it found one difference the recorded cases had missed (below) and none since.

## Where it differs from CPython

- **Set order.** CPython prints a set in the order of its hash table, which for text members
  changes from run to run. This crate prints members in insertion order. Each side reads what
  the other writes (ADR-013).
- **Unicode version.** `repr()` escapes what `str.isprintable()` rejects, and `\N{...}` knows only
  the interpreter's characters. Both are tied to the Unicode version CPython was built with, so
  `tables.rs` is generated from the recording interpreter (CPython 3.11.18, Unicode 14.0) by
  `rust/harness/gen_tables.py`. A deployment on another Python prints newer characters
  differently; both forms read back the same. The check that makes a full-width `ｓｅｔ()` an empty
  set uses the `unicode-ident` crate, which follows a newer Unicode.
- **NaN as a key.** Python finds a NaN dict key by object identity. Values here have no identity,
  so every NaN is its own key.
- **Lone surrogates.** Text like `'\ud83d'` reads as a `str` Python can hold but no backend can
  store. It is kept as code points (`PyValue::Surrogates`) and printed with the escape.
- **Int size.** CPython refuses to print or read an int of more than 4,300 digits unless told
  otherwise (`sys.set_int_max_str_digits`). The limit here is fixed at 4,300.

The difference the fuzzer found and that is now fixed: a float exactly halfway between two
shortest decimal forms, such as `900719925474099.25`. CPython prints the one ending in an even
digit (`...099.2`); Rust's own formatter prints `...099.3`.

## Checks

```sh
cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test
rust-anything gate ../dbvalue-rs
python3 -W ignore ../harness/fuzz_dbvalue.py 1 60
```
