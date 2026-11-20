# strings-rs

The bridge that proves the language strings in `rust/ultroid-core` against the Python original:
`strings/__init__.py`, which loads the language files and answers `get_string`, `get_help` and
`get_languages`. What they do is in that crate's README.

The module keeps what it loaded, changes it as it goes, and reads the database, the environment,
the folder `strings/strings` and Google's translator. So one call proves little, and it is
proven as scenarios, as the database accessors are (ADR-015). `rust/harness/language.py`
imports the original afresh for each scenario, in a folder that holds the scenario's files, with
the scenario's language in the database and in `LANGUAGE`, and with a translator that does what
the scenario says. It reports, in order, every result, every call to the translator, every
line logged, and at the end the language and everything loaded.

| Function | What it returns |
| --- | --- |
| `run(setup, steps)` | for each step `["ok", type, text]` or `["error", exception]`, with `["translate", text, language]` and `["log", kind, what]` before it as they happened, and at the end `["state", language, loaded]` |

One thing is replaced: the reader of a language file. The files are there, and the module's own
`open`, `os.path.exists` and `glob` see them, but what reading one gives is what the scenario
says it holds. Ultroid has two readers that disagree, and which is meant is not for this port
to say (ADR-018, `rust/research/language-files.md`).

## Proof

`cases.jsonl` holds 1,716 scenarios recorded from the original (`make_inputs.py` and
`rust/harness/language_scenarios.py`, seeded):

- English alone; another language with English beside it, before and after the list of
  languages is asked for; a language with no file; the language changed while running.
- Every way the translator can answer: the text, text with a place to fill in lost or gained,
  nothing, something that is not text, and each kind of failure.
- The language taken from the database, from `LANGUAGE`, from both; stored text that reads as a
  number, a list or `None`; language names that are paths.
- Files that cannot be read, files that hold a list, a number or nothing instead of a mapping,
  values that are not text, names in the folder that are no language file.
- Steps and settings that make no sense.
- 1,400 random scenarios.

1,494 scenarios run to their end, with 6,892 steps between them: 5,990 give a result and 902
fail as the original fails (`TypeError`, `KeyError`, `AttributeError`, `IndexError`). They call
the translator 1,038 times and log 743 lines. 222 scenarios fail before the module runs, on a
setting that is none.

- `rust-anything diff`: 1716/1716 match.
- `rust-anything gate`: passed.
- `rust/harness/check_shadow.py`: the recorded result comes back in `old`, `shadow` and `new`
  mode.
- `rust/harness/coverage_strings.py`: the scenarios run 51 of the 52 statements of
  `strings/__init__.py`. The one left is the import of the second reader.
- `rust/harness/fuzz_strings.py`: three seeded runs, 105,599 random scenarios (476,232 steps,
  65,147 calls to the translator), no difference.

`rust-anything bench` measures 9.14x (657 µs against 72 µs a scenario, Linux x86_64, CPython
3.11, 2026-11-20). The Python side makes a folder and imports the module for every scenario, so
the number says nothing about a lookup.

## What is not covered

- Reading a language file: YAML, or what the fallback makes of it (ADR-018).
- The translator itself. `translate` of `pyUltroid/fns/tools.py` asks Google over the network
  and waits up to a minute for it; here it is whatever the scenario says.
- A language file changed while the program runs, and two things asking for strings at once.
- Values a YAML file can hold that have no place among the values of this port: dates and
  times.
- A folder that lists its files in another order. `get_languages` loads them in the order the
  folder gives them, which is the machine's; the scenarios fix it.

## Loop

```sh
python3 make_inputs.py > inputs.jsonl
rust-anything record . --inputs inputs.jsonl
rust-anything build . && rust-anything diff . && rust-anything gate .
python3 -W ignore ../harness/fuzz_strings.py 1 40
```
