# command-rs

The bridge that proves command recognition in `rust/ultroid-core` against the Python original:
Ultroid's `compile_pattern` (`pyUltroid/_misc/_decorators.py`) and what Python's `re` makes of
the pattern it builds. What they do is in that crate's README.

`rust/harness/command.py` calls the original and reports what happened as data:

| Function | What it returns |
| --- | --- |
| `command(pattern, handler, text)` | for `ultroid_cmd(pattern=pattern)` under a handler, on a message: `["always"]` for a plugin without a pattern, `["bad pattern"]` where `re` refuses the pattern, `["no"]`, or `["match", end, groups, named groups]` |
| `assistant(pattern, text)` | the same for `asst_cmd(pattern=pattern)`, which compiles `^/` and the pattern |
| `inline(pattern, text)` | the same for `in_pattern(pattern)`, which uses the pattern as it is |

## Proof

`cases.jsonl` holds 9,301 calls recorded from the original (`rust/harness/command_inputs.py`,
seeded):

- Every pattern the code registers, read out of `plugins/`, `assistant/` and `pyUltroid/` with
  `ast`: 291 of `ultroid_cmd`, 15 of `asst_cmd`, 23 of `in_pattern`. Each under the handlers
  `.`, `/`, `!` and none, on messages built from the pattern itself: a text it accepts, the
  same with something added, dropped or changed, and text that has nothing to do with it.
- A sample of them under 26 more handlers: letters and digits (which `re` reads as escapes),
  `\`, `(`, `[`, `|`, `$`, `^`, handlers of two characters, non-ASCII ones, the empty one.
- 1,200 made-up patterns from the same grammar, with what the registered ones do not have:
  lazy repeats, counts, references to a group, groups inside loops, loops that can go round
  without taking a character, and things `re` refuses.
- rust-anything's own inputs for ports of regular expressions: text with non-ASCII word
  characters, and pairs that differ only in case.

4,113 of the cases are a match (2,183 with a group that took part), 4,036 no match, 1,073 a
pattern `re` refuses, 79 a plugin without a pattern. They use 1,718 different patterns: 836
with a lazy repeat, 952 with a count, 161 with a reference to a group.

The port declines what it does not read (ADR-017), and a declined pattern is no case:
`make_inputs.py` runs the built port on every input and leaves those out. That was 100 of
8,600: 66 for a `(?` group other than `(?:` and `(?P<` (look-around, flags, comments, atomic
groups), 16 for a group name that is not plain ASCII, 14 for a count `re` finds too large, 4
for a possessive repeat. No registered pattern may be among them under `.`, `/`, `!` or no
handler: the script stops if one is.

- `rust-anything diff`: 9301/9301 match.
- `rust-anything gate`: passed.
- `rust/harness/check_shadow.py`: the recorded result comes back in `old`, `shadow` and `new`
  mode.
- `rust/harness/fuzz_command.py`: six seeded runs of four minutes, 1,505,819 generated cases,
  no difference. 17,285 patterns were declined, and 85 cases were given up as too slow. Six of
  the 85 were too slow on one side only, each close to the limit of four seconds; with the
  slower side given twenty (seeds 1, 2 and 5 again) none was left.
- `rust/harness/command_versions.py`: the recorded cases get the same answers from the `re` of
  CPython 3.11.18 (the one recorded from), 3.12.3 and 3.13.18.

`rust-anything bench`, original against Rust with the call into Rust included (Linux x86_64,
CPython 3.11, 2026-11-20):

| Function | Python ns/call | Rust ns/call | Speedup |
| --- | ---: | ---: | ---: |
| `command` | 14009 | 1740 | 8.05x |
| `assistant` | 949 | 918 | 1.03x |
| `inline` | 25304 | 2052 | 12.33x |

Overall 4.68x, nearly all of it from compiling the pattern. Both sides are asked to compile
on every call, but `re` keeps the last 512 patterns it compiled: room for the 127 patterns of
the `assistant` cases, where the two come out even although the port compiles each time, and
not for the others. A bot compiles each pattern once. In matching alone the two are close: on
a pattern from the fuzz that took Python 4.09 seconds, the port took 4.19.

## What the fuzz found

The first port translated the pattern for a Rust regular expression engine. Every recorded
case matched; the fuzz then found ten wrong answers, all in made-up patterns: a lazy repeat
inside a repeated group, and loops whose body can match nothing. One cause was a rewrite the
engine does to patterns before running them, the other the way it defines such loops
(ADR-017). The matcher that replaced it follows CPython's, and the generator now writes
counts and references too. None of the registered patterns was affected.

A later run found a case Python answered at once and the new matcher could not finish:
`(\S*?-*)+?(b{2,3}?\[+){3}.{100001}` on a short text. `re` first looks whether the text is long
enough for the pattern at all, and so never starts on the loops in front. The matcher does the
same now, and the fuzz reports a case that is slow on one side only.

## What is not covered

- Which handler is in force (`HNDLR`, `SUDO_HNDLR`, `DUAL_HNDLR` come from the database), who
  may use a command, and what a command does once it is recognised (ADR-005).
- The patterns of `callback(...)`. They are matched against bytes, where `\w`, `\d` and `\s`
  are ASCII; this port reads patterns for text.
- Patterns with flags, look-around, conditions, atomic groups, possessive repeats, references
  by name, `\N{...}` or comments: declined, not answered.
- Text or patterns with half of a surrogate pair. Python can hold one, Rust text cannot.
- How long a match takes. On a pattern with loops inside loops both sides can take longer than
  anyone waits; the fuzz stops such a case and counts it.
- Python before 3.11. That version added possessive repeats to `re` and corrected what a
  group holds after some loops; nothing older was compared.

## Loop

```sh
rust-anything build . && python3 -W ignore make_inputs.py > inputs.jsonl
rust-anything record . --inputs inputs.jsonl
rust-anything diff . && rust-anything gate .
python3 -W ignore ../harness/fuzz_command.py 1 60
```
