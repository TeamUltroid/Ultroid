# multi_client

Ultroid's launcher as a Rust binary: what `python3 multi_client.py` does (ADR-019). It reads
the environment, starts `python3 -m pyUltroid ...` once for every client that is configured and
waits for them all. Which clients those are is `ultroid_core::launch`; what that module's README
says about the variables holds here.

Nothing in Ultroid starts this binary. It is here to be tried:

```sh
cargo build --release
cd /path/to/Ultroid          # the clients are found from the working directory, as with the script
API_ID=... API_HASH=... SESSION=... REDIS_URI=... REDIS_PASSWORD=... path/to/multi_client
```

## Where it differs from the script

- **The interpreter.** The script starts each client with the interpreter it runs under
  itself. The binary uses `python3` from `PATH`, or what the variable `PYTHON` names. With a
  virtual environment, activate it or set `PYTHON` to its interpreter.
- **An interpreter that cannot be started** is said so on the error output, the clients
  already started are waited for, and the status is 1. The script cannot fail there.
- `RUST_ANYTHING_UNIT_LAUNCH=original` makes the binary run the script instead. That needs the
  checkout it was built in, and `python3`.

Everything else is the script's: arguments on the command line are ignored, a client that
fails changes nothing, and the status is 0 once every client has ended.

## Proof

`../app-cases` holds 13 runs recorded from `python3 multi_client.py`
(`../harness/app_cases.jsonl` are the inputs): nothing configured, a client missing one
variable or holding an empty one, variables the script does not read, one client, the second
alone, the first and the third, all five, a client that fails, values with blanks and quotes
in them. Where clients are started, the case brings a stand-in for the bot, a
`pyUltroid/__main__.py` that prints the arguments it got, so that a case shows what the
launcher did.

```sh
cargo test                                   # replays the cases with trycmd; needs python3
rust-anything app replay ../.. --build target/debug/multi_client
```

Both pass 13 of 13, and none of the 13 is answered by the script.

## What is not covered

- The bot. The clients this starts are the Python program.
- Signals. What happens to the clients when the launcher is interrupted or stopped was not
  recorded; neither the script nor the binary does anything about it.
- Output of several clients at once. In the cases the stand-ins take turns; real clients
  write when they write, with the script and with the binary alike.
