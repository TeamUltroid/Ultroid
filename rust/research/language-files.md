# Language files: two readers, two results

Checked on 2026-11-20 against the repository at this branch, with CPython 3.11.18 and PyYAML
6.0.3. Every number below comes from `rust/harness/compare_readers.py`; run it to see the keys.

## Which reader runs

`strings/__init__.py` (lines 9 to 12):

```python
try:
    from yaml import safe_load
except ModuleNotFoundError:
    from pyUltroid.fns.tools import safe_load
```

PyYAML is in neither `requirements.txt` nor `resources/startup/optional-requirements.txt`. The
workflow that checks the strings (`.github/workflows/stringanalysis.yml`) installs it with
`pip install pyyaml`. So an installation from the requirements reads the language files with the
fallback, unless something else brought PyYAML along, and the check in CI reads them with
PyYAML. Whether the image the `Dockerfile` starts from has PyYAML could not be seen from here.

## How the fallback reads

`safe_load` and `_get_value` in `pyUltroid/fns/tools.py` (lines 1052 to 1082): the file is
taken line by line. A line with a `:` is a key and a value, split at the first `:`. A line with
a `-` and no `:` is an item of the list under the key before it. The value is passed to `eval`;
when that fails, the text of the value is kept as it stands. An empty value becomes `[]`.

## What comes out differently

138 of the 11,824 keys in the 24 files, in 15 languages:

| Language | Keys that differ | Language | Keys that differ |
| --- | ---: | --- | ---: |
| `ml` | 23 | `ar` | 8 |
| `gu` | 19 | `bn` | 4 |
| `it` | 19 | `uz` | 3 |
| `si` | 18 | `es` | 1 |
| `hi` | 16 | `fa` | 1 |
| `cn` | 12 | `jp` | 1 |
| `ka` | 11 | `ms` | 1 |
| | | `or` | 1 |

`az`, `en`, `fr`, `id`, `mr`, `pt-br`, `ru`, `ta` and `tr` come out the same.

Three things cause it:

- **A value written over more than one line is cut after the first.** YAML joins the lines of a
  quoted value. The fallback sees the first line only: an opening quote with no closing one,
  which `eval` cannot read, so the text is kept as it stands, quote and all, with `\n` as a
  backslash and an `n`. `afk_2` in `ms.yml`:

  ```
  PyYAML:   '#AFK\nSet mod AFK kepada **tidak aktif**\n Tidak ada untuk `{}`'
  fallback: '"#AFK\\nSet mod AFK kepada **tidak aktif**\\n'
  ```

  The message loses its `{}`, so the `.format(...)` that fills it in gives the cut text back
  without the value.
- **The other lines of such a value become keys.** Each of them that holds a `:` is taken for a
  key of its own. `cn.yml` gets six keys that are not keys, among them `**Used` with the value
  `{}  Free: {}\n\n**`. `hi.yml` gets thirteen.
- **`\ ` is kept.** In YAML a backslash and a blank in a quoted value are a blank. Python's
  `eval` keeps both characters. `clst_2` in `es.yml` reads `... éxito! \ NReinicio ...` with
  the fallback. (These are line breaks a translator mangled; `get_string` mends `\ N` in what
  it has translated itself, not in what a file holds.)

## The fallback evaluates the file

Every value goes through `eval` in the namespace of `pyUltroid/fns/tools.py`. Of the values in
the 24 files today, 11,622 are text in quotes and come out as that text; 341 are not Python
(`English`, an author's name, text with an opening quote only) and are kept as they stand. None
evaluates to anything else.

But a value that is a Python expression is evaluated. An author who goes by `max` would be
listed as `<built-in function max>`; a value such as `__import__("os").system(...)` would run.
The files come from the same repository as the code, so this lets nobody run code who could not
already, but it does mean a change to a translation has to be read as a change to code.

## What this means for the port

The two readers are two behaviours of the same program, and which one a deployment has depends
on a package nobody asked it to install. A Rust Ultroid has to pick one. Reading the files as
YAML is what the files are written for and what CI checks; reading them as the fallback does
is what a plain installation does today, cut strings included. That is the maintainers' call
(ADR-018), and until it is made the port takes what a file holds as given and proves what
happens from there (`rust/strings-rs`).

A fix on the Python side that needs no decision here: add `pyyaml` to `requirements.txt`.
