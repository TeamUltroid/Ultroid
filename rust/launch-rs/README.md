# launch-rs

The bridge that proves the launch logic in `rust/ultroid-core` against the Python original:
`multi_client.py`, the script that starts up to five Ultroid clients from one environment. What
it does is in that crate's README.

The script has no function to call: it reads the environment, starts the clients and waits.
`rust/harness/launch.py` runs the script itself, with the given variables in place of the real
environment and a `subprocess.Popen` that notes what it is asked to start and starts nothing.

| Function | What it returns |
| --- | --- |
| `plan(environment)` | `["start", arguments, ...]` with the arguments of each client the script starts, in order, or `["exit", message]` when it leaves because none is configured |

## Proof

`cases.jsonl` holds 1,714 runs recorded from the original (`make_inputs.py`, seeded):

- Each client alone, with each of its five variables missing and with each one empty.
- Every set of clients from the first to the fifth, in both orders of the variables.
- Variables the script does not read next to ones it does: a suffix of `5`, `0` or `01`,
  lower case, blanks around the name, `REDIS_URL`.
- Values with blanks, line breaks, quotes, non-ASCII text, a leading `-`.
- 1,500 random environments.
- What is no environment: a list, a number, a dict with a value that is not text.

893 runs start clients (627 one, 207 two, 47 three, 10 four, 2 five), 802 leave with the
message, 19 fail in the harness on what is no environment.

- `rust-anything diff`: 1714/1714 match.
- `rust-anything gate`: passed.
- `rust/harness/check_shadow.py`: the recorded result comes back in `old`, `shadow` and `new`
  mode.
- `rust/harness/fuzz_launch.py`: three seeded runs, 191,287 random environments (7,348 with a
  client to start), no difference.

`rust-anything bench` measures 12.81x (172 µs against 13 µs a call, Linux x86_64, CPython 3.11,
2026-11-20). The Python side runs the whole script each time, so the number says little, and
this runs once at start.

## What is not covered

- Starting the clients and waiting for them. The harness checks that the script starts each
  with its own interpreter and waits for every one; the port gives the arguments, and a
  launcher has to run them.
- What a client does with its arguments. `pyUltroid/configs.py` reads them by position and
  turns the first into a number; a client given an `API_ID` that is no number fails there.
- Variables that are not text. An environment holds bytes; the Rust function takes any value
  that can be an argument (`OsStr`), the cases are text.

## Loop

```sh
python3 make_inputs.py > inputs.jsonl
rust-anything record . --inputs inputs.jsonl
rust-anything build . && rust-anything diff . && rust-anything gate .
```
