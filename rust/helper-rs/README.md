# helper-rs

Rust port of the number-formatting functions in `pyUltroid/fns/helper.py`, bridged with PyO3.

| Function | Original | Used for |
| --- | --- | --- |
| `time_formatter` | `pyUltroid/fns/helper.py:501` | uptime, ETA and elapsed times in messages |
| `humanbytes` | `pyUltroid/fns/helper.py:521` | file sizes and transfer speeds |
| `numerize` | `pyUltroid/fns/helper.py:535` | view and like counts |

The other 16 names in that file stay in Python: they take Telethon objects, run a shell or `git`,
transfer files or restart the process. `rust-anything.json` lists each with its reason.

## Proof

`cases.jsonl` holds 213 calls recorded from the Python original: rust-anything's generated edge
cases (NaN, infinities, signed zero, the largest float) plus the values in `inputs.jsonl`, which
follow what the callers pass (durations in milliseconds, byte counts, counts that may be `None`).

- `rust-anything diff`: 213/213 match.
- `rust-anything gate`: passed (fmt, clippy, tests, no `unsafe`, no panics on error paths).
- `rust/harness/check_shadow.py`: the shadow drop-in returns the recorded result in `old`,
  `shadow` and `new` mode, with no mismatch reported.

`rust-anything bench`, original against Rust with the call into Rust included (Linux x86_64,
CPython 3.11, 2026-11-20):

| Function | Python ns/call | Rust ns/call | Speedup |
| --- | ---: | ---: | ---: |
| `time_formatter` | 708 | 612 | 1.16x |
| `humanbytes` | 735 | 770 | 0.95x |
| `numerize` | 705 | 683 | 1.03x |

These functions are too small for Rust to matter: the port is here for correctness, as the
formatting a Rust Ultroid will need, not for speed.

## Behaviour of the original that the port keeps

- A value still too large after the last unit is divided once more: 1024 TB prints as `1.00TB`,
  and `numerize(10**15)` is `1.00T`.
- Negative durations borrow from every unit: `time_formatter(-5000)` is `-1w:6d:23h:59m:55s`.
- Ints below the first step print without decimals (`1023B`, `999`); everything else has two.
- `humanbytes(None)` is `0 B`; `numerize(None)` and `numerize(0)` are `None`.
- NaN and infinities print as `nanTB`, `infTB`, `-infB`; `time_formatter` raises `ValueError`
  for NaN and `OverflowError` for infinities.

## Where the port differs outside the recorded cases

- A Python int beyond 64 bits is refused with `OverflowError`; the original accepts it.
- `True` is treated as `1`: `humanbytes(True)` is `1B` and `numerize(True)` is `1`, where the
  original gives `TrueB` and `True`.
- An empty string or list is refused with `TypeError`; for any falsy value the original's
  `humanbytes` returns `0 B` and its `numerize` returns `None`.

Ultroid's call sites pass durations, sizes, speeds and counts, so none of this is reached today.

## Loop

```sh
rust-anything record . --inputs inputs.jsonl   # the original's behaviour -> cases.jsonl
rust-anything build .                          # the PyO3 module
rust-anything diff .                           # recorded cases against Rust
rust-anything shadow .                         # drop-in for this checkout (not committed)
rust-anything gate .                           # the definition of done
```
