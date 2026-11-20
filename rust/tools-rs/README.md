# tools-rs

Rust port of the text functions in `pyUltroid/fns/tools.py`, bridged with PyO3.

| Function | Original | Used for |
| --- | --- | --- |
| `get_msg_button` | `pyUltroid/fns/tools.py:176` | `[label\|url]` button markup in notes, filters, snips and broadcasts |
| `text_set` | `pyUltroid/fns/tools.py:319` | laying text out on a page in the writer plugin |
| `stdr` | `pyUltroid/fns/tools.py:543` | `HH:MM:SS` positions for the audio and video tools |
| `cmd_regex_replace` | `pyUltroid/fns/tools.py:730` | turning a command pattern into a name for `help` |
| `get_chat_and_msgid` | `pyUltroid/fns/tools.py:1085` | reading a chat and message id out of a message link |

The other 28 names in that file stay in Python: they call web APIs, run `mediainfo`, touch the
filesystem, or take Telethon and OpenCV objects. `rust-anything.json` lists each with its reason.
`json_parser` is one of them for now: its contract is Python's `json` and `ast.literal_eval`,
which the database value format needs first.

## Proof

`cases.jsonl` holds 809 calls recorded from the Python original: rust-anything's generated cases
(for `get_msg_button`, 211 strings with non-ASCII text and regex traps) plus the 537 in
`inputs.jsonl`. Those include all 291 distinct command patterns the plugins register with
`ultroid_cmd`, which is what `help` passes to `cmd_regex_replace`, and message links with the
shapes users paste.

- `rust-anything diff`: 809/809 match.
- `rust-anything gate`: passed.
- `rust/harness/check_shadow.py`: the recorded result comes back in `old`, `shadow` and `new`
  mode, with no mismatch reported.

`rust-anything bench`, original against Rust with the call into Rust included (Linux x86_64,
CPython 3.11, 2026-11-20):

| Function | Python ns/call | Rust ns/call | Speedup |
| --- | ---: | ---: | ---: |
| `get_msg_button` | 930 | 874 | 1.06x |
| `text_set` | 834 | 1827 | 0.46x |
| `stdr` | 902 | 1086 | 0.83x |
| `cmd_regex_replace` | 348 | 1004 | 0.35x |
| `get_chat_and_msgid` | 1157 | 919 | 1.26x |

Overall 0.71x. rust-anything's verdict: do not ship this unit for speed, because crossing into
Rust costs more than the work these functions do. Nothing here is wired into the app (ADR-012);
the port is the proven text handling a Rust Ultroid will need, where there is no crossing.

## Behaviour of the original that the port keeps

- `get_msg_button`: `[label|url|same]` joins the row above, and raises `IndexError` when there
  is no row above. `[|]` is a button with an empty label and URL, but its markup stays in the
  text. Markup does not span lines. The text is stripped the way Python strips it, which
  includes the separators U+001C to U+001F.
- `text_set`: 55 characters to a line and 25 lines at most. A line whose length is an exact
  multiple of 55 is followed by an empty line. Text of 55 characters or fewer comes back whole,
  newlines included. Any other value that has a length of 55 or less comes back as a one-item
  list, as the original only asks for a length.
- `stdr`: ints give `01:01:01`; floats keep their decimals and a zero field drops out, so
  `stdr(60.0)` is `00:1.0:`. Negative values borrow: `stdr(-1)` is `-1:59:59`.
- `cmd_regex_replace`: `?(\d+)` is never removed, because the brackets are stripped before it is
  tried: `purge ?(\d+)` becomes `purge ?\d+`.
- `get_chat_and_msgid`: only the first link counts. `t.me/c/123` with nothing after it reads as
  chat `c`, message `123`. A `/c/` id goes through Python's `int("-100" + id)`, so `12_3`,
  trailing whitespace and digits of any script are accepted, and anything else raises
  `ValueError`.

## A difference the first recording missed

The first version of this port passed its gate with 789 cases and was still wrong. `stdr` prints
a float with Python's `repr`, the shortest digits that read back as the same number. For a float
exactly halfway between two such forms, CPython takes the one ending in an even digit and Rust's
formatter takes the upper one: `stdr(16.0000152587890625)` is `00:00:16.000015258789062` in
Python and was `...063` here. The fuzzer of the database value format found the rule
(`rust/ultroid-db`); this port had the same code. It is fixed, and 20 such floats are now in
`inputs.jsonl`, 14 of which the first version got wrong.

A passing gate proves the recorded cases, not the function.

## Where the port differs outside the recorded cases

- A Python int beyond 64 bits passed to `stdr` is refused with `OverflowError`; the original
  accepts it.
- Text holding a lone surrogate (`"\ud800"`) cannot cross into Rust and raises
  `UnicodeEncodeError`; the original handles it as any other character.
- Digits of scripts newer than the interpreter's Unicode tables: CPython 3.11 follows Unicode
  14.0 and does not count Kawi or Garay digits as digits; the `regex` crate does. A link written
  with them parses in Rust and not in Python 3.11.

## Loop

```sh
rust-anything record . --inputs inputs.jsonl   # the original's behaviour -> cases.jsonl
rust-anything build .                          # the PyO3 module
rust-anything diff .                           # recorded cases against Rust
rust-anything shadow .                         # drop-in for this checkout (not committed)
rust-anything gate .                           # the definition of done
```
