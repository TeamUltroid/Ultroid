# Core dependencies: Rust stand-ins and compatibility traps

Surveyed on 2026-11-20 with `cargo 1.97.0` and a virtual environment on CPython 3.11.18. Scope: the Python
packages behind `pyUltroid/`, `strings/` and the start-up path. Plugin-only packages are in
`dependencies-plugins.md`. No Rust was compiled or run: crate behaviour comes from registry metadata,
documentation and published source. Python behaviour comes from package source and, where marked
**run**, from running the installed package (or the repository's own function) on throwaway input
outside the repository.

Source tags, one per claim:

- `R:<crate>-<ver>/<file>:<line>`: crate source as cargo unpacked it under
  `~/.cargo/registry/src/index.crates.io-*/`. docs.rs serves the same files at
  `https://docs.rs/crate/<crate>/<ver>/source/<file>` (checked for dotenvy `src/parse.rs` and
  serde_yaml_ng `src/de.rs`).
- `V:<path>`: installed package under the environment's `site-packages/`.
- `W:<pkg> <ver>/<path>`: file in that version's wheel or sdist from `https://pypi.org/project/<pkg>/<ver>/#files`,
  unpacked and read, not installed. redis, pymongo, psycopg2, apscheduler, pytz, heroku3, coloredlogs,
  psutil and localdb.json are not in the venv.
- **ci**: `cargo info <crate>` (version, licence). It reports pre-releases and, for a newer MSRV, an
  older version; both cases are flagged. **io**: `https://crates.io/api/v1/crates/<crate>` (release dates).
- Paths without a tag are in this repository. URLs were read on the survey date.

Fit: `good` = every call Ultroid makes has a counterpart and the differences are settings. `partial` =
calls are missing or results are known to differ. `none` = no usable crate. `not verified` = could not
be confirmed.

## Summary

Compatibility traps were found in:

- **Stored value format** (`ast.literal_eval` / `str()`): no crate pairs an equivalent reader with an equivalent writer. `py_literal` reads `007`, `2021-12-25` and `1+2` as numbers where Python keeps the text, and prints floats, quotes and non-ASCII differently.
- **`localdb.json`**: the PyPI release writes a Python dict `repr` and reads it with `eval`; the repository's main branch writes JSON. Deletes are not written to disk in the release.
- **`psycopg2` layout**: one unquoted column per key (names fold to lower case, 63-byte limit, 1,600-column limit that counts dropped columns); reading a key after writing it returns a string on this backend only.
- **`python-decouple` + `python-dotenv`**: up to three parsers read `.env` today (bash, python-dotenv, decouple). `dotenvy` differs from each on spaces, `$`, backslashes, `#`, duplicates and malformed lines. An empty value is not "unset": `LOG_CHANNEL=` raises.
- **`pyyaml`**: PyYAML is not a declared requirement, so the reference is PyYAML or a built-in fallback that disagrees on 83 keys. The YAML 1.1 scalar rules differ in every Rust crate read, but no such scalar occurs in the 24 files.
- **`redis`**: `REDIS_URI` is `host:port`, which the crate's URL parser rejects; its async default timeout is 500 ms; `cargo info` reports a release candidate.
- **Defaults** in HTTP, scheduler, time zones, git, logging: proxy variables, `User-Agent`, timeouts, decompression, UTC cron, zone-name case, transports off by default, level names.
- Unused in the core: the `apscheduler`, `certifi` and `ssl` imports. `psutil` is plugin-only.

## 1. `redis`

**Use.** `RedisDB` (`pyUltroid/startup/_database.py:245-298`), created at `:335-343` with `decode_responses=True, socket_timeout=5, retry_on_timeout=True`. Commands sent: `SET key value` (`:286`, from `set_key` `:99`), `GET` (`:287`, `:86`), `KEYS *` (`:288`; `re_cache` `:65`; `pyUltroid/startup/funcs.py:106`), `DEL` (`:289`, `:81`), `MEMORY USAGE` per key (`:298`). `ping()` is the base method and returns 1 without contacting the server (`:68-69`); `rename` is GET + DEL + SET (`:101-107`). No expiry, pipelines, hashes or pub/sub.

- `REDIS_URI` is `host:port`, split on `:` (`:256-259`); a value starting with `http` exits (`:260-264`); the password is a separate variable (`:337`); `REDISUSER` is read (`pyUltroid/configs.py:51`) and never passed; no TLS and database 0, by redis-py's defaults (W:redis 8.1.0/redis/client.py:272, 292).

**Candidate.** `redis`: ci reports 2.0.0-rc.3 (pre-release, BSD-3-Clause, MSRV 1.96). The newest stable is 1.8.2 (https://index.crates.io/re/di/redis; `cargo info redis@1.8.2`: BSD-3-Clause, MSRV 1.88). Both released 2026-11-14 (io). 1.8.2 was read.

**Fit: good.** `get`, `keys`, `set`, `del` are typed commands (R:redis-1.8.2/src/commands/mod.rs:275, 287, 293, 362). `MEMORY USAGE` has no typed helper in that file; the generic `redis::cmd(..)` form is shown at R:redis-1.8.2/src/client.rs:152-155.

Traps:
- `Client::open(&str)` accepts only the schemes `redis`, `rediss`, `valkey`, `valkeys`, `redis+unix`, `valkey+unix`, `unix`; anything else is "Redis URL did not parse" (R:redis-1.8.2/src/connection.rs:151-161, 525-531). Ultroid's `host:port` is none of these. A `(host, port)` tuple is accepted (`:534-545`).
- A password inside a URL is percent-decoded (R:redis-1.8.2/src/connection.rs:672-681); Ultroid passes the password verbatim.
- Async connections default to a 500 ms response timeout and a 1 s connect timeout (R:redis-1.8.2/src/client.rs:181-184, 249-253); Ultroid asks for 5 s. redis-py 8.1.0 also retries, 10 attempts with backoff by default, and marks `retry_on_timeout` deprecated (W:redis 8.1.0/redis/_defaults.py:37-39; redis/client.py:284-290, 343).
- Text: redis-py decodes replies as UTF-8 with `encoding_errors="strict"` (W:redis 8.1.0/redis/client.py:281-283); `String: FromRedisValue` uses `from_utf8` (R:redis-1.8.2/src/types.rs:1997-2012). Same rule.
- `KEYS *` returns every key of the database, not only Ultroid's (W:redis 8.1.0/redis/commands/core.py:3537-3545). The redis-py version on deployments is not pinned (`_database.py:25`, `installer.sh:190`).

## 2. `pymongo`

**Use.** `MongoDB` (`_database.py:110-151`): database `UltroidDB` (`:111-113`); **one collection per key**, holding one document `{"_id": <key>, "value": str(value)}` (`:134-139`); read with `find_one({"_id": key})["value"]` (`:144-146`); delete drops the collection (`:141-142`); `keys()` is `list_collection_names()` (`:131-132`); `usage` is `dbstats.dataSize` (`:123-125`); `ping` is `server_info()` (`:127-129`); `flushall` drops the database by its literal name (`:148-151`). Option `serverSelectionTimeoutMS=5000` (`:112`).

**Candidate.** `mongodb` 3.10.2, Apache-2.0 (ci), released 2026-11-19 (io).

**Fit: good.** `list_collection_names`, `find_one`, `replace_one`, `insert_one`, `drop`, `run_command` exist (R:mongodb-3.10.2/src/action/list_collections.rs:53, find.rs:55, replace_one.rs:30, insert_one.rs:32, drop.rs:23, 82, run_command.rs:42).

Traps:
- `_id` is the key string, not an ObjectId (`_database.py:136-138`).
- An existing collection is updated with `replace_one` and no upsert (`_database.py:135-136`; default `upsert=False`, W:pymongo 4.20.1/pymongo/synchronous/collection.py:1118): a collection that exists without its document is never filled.
- `keys()` returns every collection of the database, system collections included unless filtered (W:pymongo 4.20.1/pymongo/synchronous/database.py:1228-1231).
- Server selection waits 30 s by default (R:mongodb-3.10.2/src/client.rs:65; src/client/options.rs:681-685), not 5 s.
- Trust store: PyMongo loads the system CA store (`ctx.load_default_certs()`, W:pymongo 4.20.1/pymongo/ssl_support.py:150). The crate's default `rustls-tls` feature uses the compiled-in `webpki_roots::TLS_SERVER_ROOTS` (ci feature list; R:mongodb-3.10.2/src/runtime/tls_rustls.rs:21). A server certificate from a CA installed only on the host stops verifying.

## 3. `psycopg2`

**Use.** `SqlDB` (`_database.py:162-239`): `psycopg2.connect(dsn=url)`, autocommit (`:168-169`).

- Table: `CREATE TABLE IF NOT EXISTS Ultroid (ultroidCli varchar(70))` (`:171-173`). **One TEXT column per key.** `set` runs `ALTER TABLE Ultroid DROP COLUMN IF EXISTS {key}`, `ALTER TABLE Ultroid ADD {key} TEXT`, `INSERT INTO Ultroid ({key}) values (%s)` with `str(value)` (`:214-224`), so every write adds a column and a row. `get` runs `SELECT {key} FROM Ultroid` and returns the first non-empty cell (`:201-212`). `delete` drops the column (`:226-231`). `keys()` reads `information_schema.columns` for table `ultroid` (`:194-199`). `usage` takes the number out of `pg_size_pretty(..)` and drops the unit (`:186-192`).
- Key names are pasted into the SQL text unquoted.

**Candidates.** `tokio-postgres` 0.7.18 and `postgres` 0.19.14, MIT OR Apache-2.0 (ci), released 2026-06-12 (io). `sqlx` 0.9.1, MIT OR Apache-2.0 (ci), 2026-11-18 (io); this is the mapping in `rust/PLAN.md:127`.

**Fit: partial.** The statements are plain SQL. The rules below belong to Ultroid's layout and must be reproduced by hand, and connection strings are not accepted the same way.

Traps:
- "Quoting an identifier also makes it case-sensitive, whereas unquoted names are always folded to lower case" (https://www.postgresql.org/docs/current/sql-syntax-lexical.html). Key `LOG_CHANNEL` lives in column `log_channel`; `keys()` returns lower-case names plus `ultroidcli`. A port that quotes identifiers in their original case finds no existing data.
- Identifiers "must begin with a letter ... or an underscore", continue with letters, digits, `_`, `$`, and are truncated to 63 bytes (same page). Other keys are syntax errors; `get` catches only `UndefinedColumn` (`_database.py:204`).
- "columns per table: 1,600" and "Columns that have been dropped from the table also contribute to the maximum column limit" (https://www.postgresql.org/docs/current/limits.html). Each `set` drops and adds a column, so by that rule a table has a limited number of writes until `flushall` recreates it (`:233-239`). Not tested against a server.
- Read after write (**run**, the repository's `_BaseDatabase` and `SqlDB` on a stub cursor): `SqlDB.set` puts the string it was given into the cache (`_database.py:221`, called from `:99`), so `get_key("SUDOS")` after `set_key("SUDOS", [1, 2])` returns the str `'[1, 2]'` until restart. The other backends return the list (`:96`).
- psycopg2 merges arguments into the SQL text on the client ("exactly the one that would be sent", W:psycopg2 2.9.13/doc/src/cursor.rst:253-262) and rejects NUL bytes itself (W:psycopg2 2.9.13/psycopg/utils.c:62). tokio-postgres passes `$n` parameters separately from the statement (R:tokio-postgres-0.7.18/src/client.rs:245); what a NUL byte produces there was not verified.
- DSN: psycopg2 passes a libpq string, keyword/value or URI (W:psycopg2 2.9.13/lib/__init__.py:84-112; doc/src/module.rst:86). tokio-postgres takes both forms (R:tokio-postgres-0.7.18/src/config.rs:107-109, 196) but only `sslmode` `disable`, `prefer`, `require`, and fails on unknown options (`:119-120, 583-591, 715-719`); TLS needs a separate crate, `NoTls` otherwise (R:tokio-postgres-0.7.18/src/lib.rs:93-98). sqlx documents the URL form only, knows the six libpq `sslmode` values with default `prefer`, and ignores unknown parameters with a warning (R:sqlx-postgres-0.9.1/src/options/doc.md:3-4, 35; ssl_mode.rs:8-48; parse.rs:106).

## 4. `localdb` (PyPI name `localdb.json`)

**Use.** `LocalDB` (`_database.py:304-326`) with `Database("ultroid")`, installed by `pip install -q localdb.json` when no other backend is configured (`:41-47`). The only release on PyPI is 1.0 (2022-02-06), AGPL-3.0 (https://pypi.org/pypi/localdb.json/json).

**On disk (1.0).** File `ultroid.json` in the working directory: `.json` is appended to the name (W:localdb.json 1.0/localdb/__init__.py, `__init__`); `.gitignore:18` lists it. The content is **not JSON**: `set` does `dbfile.write(str(data))`, the `repr` of a dict, and `_data` reads it back with `eval()` (same file). Ultroid passes `str(key), str(value)` (`_database.py:99`), so the file is one Python dict literal of string keys to string values, for example `{'HNDLR': '.', 'SUDOS': '[1, 2]'}`. The file is opened without `encoding=`, which is the locale's encoding before Python 3.15 unless UTF-8 mode is on (https://docs.python.org/3/library/functions.html#open).

**Candidate.** No crate. Reading release 1.0 files needs the Python literal reader of section 5. `serde_json` 1.0.154, MIT OR Apache-2.0 (ci), covers only the JSON variant below.

**Fit: none.**

Traps:
- Two formats exist. The repository's `main` writes with `json.dump` and reads with `json.load`, falling back to `eval` (https://raw.githubusercontent.com/buddhhu/localdb.json/main/localdb/__init__.py); the PyPI 1.0 file does not import `json`. Which one a deployment has depends on how the package was installed.
- 1.0 `delete` does not write: it calls `set(delete_key=key)`, which returns before opening the file when `key` and `value` are empty (W:localdb.json 1.0/localdb/__init__.py, `set`). A deleted key is back after a restart unless another key was written in between.
- 1.0 `set` skips falsy values (`if key and value`), so `set_key(k, "")` leaves the old value in the file.
- `LocalDB.keys()` calls `_raw_data()`, which returns the file text, not a dict, and so falls through to the in-memory cache (`_database.py:316-323`): `udB.keys()` lists only keys touched in this run.
- `eval` executes whatever expression the file contains.

## 5. Stored value format

**Rule.** `set_key` parses a string value first, then stores `str()` of the result (`_database.py:94-99`). `get_key` returns `ast.literal_eval(text)` or, on any exception, the text (`:84-92`). The reader is CPython's `literal_eval`; the writer is CPython's `str()` and `repr()`.

- `literal_eval` parses a full Python expression and accepts constants (str, bytes, numbers, `True`, `False`, `None`, `Ellipsis`), tuples, lists, sets, dicts, `set()`, unary `+`/`-` on numbers, and `+`/`-` only between a real and a complex number (CPython 3.11 `Lib/ast.py:54-108`; https://docs.python.org/3/library/ast.html#ast.literal_eval). Leading spaces and tabs are stripped only since 3.10 ("Changed in version 3.10", same page); ADR-010 allows CPython 3.9.
- **run** (CPython 3.11.18, the logic of `_get_data` followed by `str()`):

| stored text | Python value | text written back |
| --- | --- | --- |
| `007`, `0123456789` | str (SyntaxError) | unchanged |
| `2021-12-25`, `1+2`, `--5`, `true`, `nan` | str (ValueError) | unchanged |
| `1_000`, `0x10`, `(1)`, space + `5` | int | `1000`, `16`, `1`, `5` |
| `1e5` | float | `100000.0` |
| `1,2` | tuple | `(1, 2)` |
| `'a' 'b'`, `u'abc'` | str | `ab`, `abc` |
| `{'a': 1, 'a': 2}` | dict | `{'a': 2}` |
| `set()`, `...` | set, Ellipsis | `set()`, `Ellipsis` |

- Writer (**run**): a top-level str is stored bare (`it's`). Inside containers `repr` chooses the quote (`["it's", 'q"']`), escapes control and non-printable characters (`\t`, `\x07`, `\xa0`, `\u200b`), keeps printable non-ASCII (`'é 日本'`, emoji included), writes floats as `7000.0`, `1e+16`, `1e-05`, complex as `(1+2j)` and the empty set as `set()`. "Printable" follows the interpreter's Unicode database (https://docs.python.org/3/library/stdtypes.html#str.isprintable): 3.11.18 has 14.0.0 and writes U+1FAE8 as `\U0001fae8`, so the text written depends on the interpreter. A set of strings prints in a different order on each run.

**Candidates.** Searches: `cargo search` for `py_literal`, `python literal`, `literal_eval`, `rustpython-literal`, `python repr`, `python-literal`, `pyliteral`; no other crate turned up.

| crate | ci, io | reads | prints |
| --- | --- | --- | --- |
| `py_literal` 0.4.0 | MIT OR Apache-2.0; last release 2021-04-07 | str, bytes, int, float, complex, tuple, list, dict, set, bool, None | yes, but not as `repr()` does |
| `rustpython-literal` 0.6.0 | MIT; 2026-10-02 | float and complex text only | pieces: str, bytes, float, complex |
| `ruff_python_literal` 0.0.23 | MIT; 2026-11-19 (ci shows 0.0.22 for rustc 1.97) | no | pieces: str, bytes, float |
| `rustpython-parser` 0.4.0 | MIT; 2024-08-06 | expression to AST | no |
| `ruff_python_parser` 0.0.23 | MIT; 2026-11-19 (ci shows 0.0.22 for rustc 1.97) | expression to AST | no |
| `pyo3` 0.30.1 | MIT OR Apache-2.0 | CPython itself | CPython itself |

`py_literal`:
- Documented types: the eleven `Value` variants, `Integer` being a `BigInt` (R:py_literal-0.4.0/src/lib.rs:67-99; https://docs.rs/py_literal/0.4.0/py_literal/enum.Value.html). `Dict` and `Set` are `Vec`s, so duplicates are kept.
- Documented as not implemented: `r`/`u` prefixes, string concatenation, newlines outside strings, parentheses other than tuples, `\N{name}` (R:py_literal-0.4.0/src/parse.rs:76-84). README: "work-in-progress ... supports only a subset" (R:py_literal-0.4.0/README.md).
- Reads more than Python (from the grammar, not run): `number_expr` adds and subtracts any numbers (R:py_literal-0.4.0/src/grammar.pest:57; src/parse.rs:215-235; its test parses `+-23 + 4.5 -+- -5j - 3e2 + 1.2 - 9`, `:440-449`), so `2021-12-25`, `1+2`, `--5` become numbers. `dec_integer = digit ("_"? digit)*` has no leading-zero rule (grammar.pest:66), so `007` reads as 7.
- Reads less than Python (from the grammar, not run): `(1)`, `(1+2j)` (what `str(complex)` writes), `1,2`, `set()`, `...`, a trailing newline or comment (grammar.pest:1, 4, 81, 106). A reader that falls back to the text keeps the text where Python returns a value.
- Printing: `Display` calls `format_ascii()` (src/lib.rs:101-110): always single quotes; non-ASCII as `\x`, `\u`, `\U` (what Python's `ascii()` does, https://docs.python.org/3/library/functions.html#ascii); tab and other control characters raw; floats in `{:e}` form; complex without parentheses; an empty set is an error (R:py_literal-0.4.0/src/format.rs:12-16, 66-104, 149-151). Its own example prints `{'foo': [5, (7e3,)], 2-5j: {b'bar'}}` (src/lib.rs:36-41); Python prints `7000.0` and `(2-5j)`.

Others:
- `rustpython-literal` has no README and no crate-level documentation (`readme = false`, R:rustpython-literal-0.6.0/Cargo.toml; src/lib.rs). `UnicodeEscape::new_repr(..).str_repr()` chooses quotes as CPython does ("always use primary unless we have primary but no secondary", src/escape.rs:76-96), escapes `\n \t \r \\`, `\xNN`, `\uNNNN`, `\UNNNNNNNN` and keeps what `rustpython_unicode::classify::is_repr_printable` accepts (`:209-262`). `AsciiEscape` does bytes (`:314-319`), `float::to_string` targets `repr(float)` (src/float.rs:327, tests `:427-448`), `complex::to_string` adds the parentheses (src/complex.rs:5-13, 37). No container code.
- `ruff_python_literal` and `ruff_python_parser`: "an internal component of Ruff. The Rust API exposed here is unstable and will have frequent breaking changes" (R:ruff_python_literal-0.0.22/README.md; R:ruff_python_parser-0.0.22/README.md).
- `rustpython-parser`: its repository says "superseded by" Ruff's parser (https://github.com/RustPython/Parser). Both parsers reject leading zeros as CPython does (R:rustpython-parser-0.4.0/src/lexer.rs:394-396; R:ruff_python_parser-0.0.22/src/lexer.rs:1070). Both stop at the AST: `grep -rn literal_eval` finds nothing in either crate's `src/`, so the `_convert` step has no counterpart there.
- `pyo3` ("Bindings to Python interpreter", ci) calls the real functions and keeps CPython as a run-time dependency.

**Fit: partial** for every candidate. None pairs a `literal_eval`-equivalent reader with a `repr()`-equivalent writer.

## 6. `python-decouple`, `python-dotenv`

**Use.** `pyUltroid/configs.py:10-57`: `load_dotenv()` runs first if importable (`:12-17`), then `config(name, default=.., cast=..)` per variable; `API_ID`, `API_HASH`, `SESSION`, `REDIS_URI`, `REDIS_PASSWORD` come from `sys.argv[1..5]` when given (`:22-38`). `update_envs` copies some variables into the database (`pyUltroid/startup/funcs.py:93-111`). `bash startup` also runs `source .env` under `allexport` (`startup:18`; `Dockerfile:20`), so shell rules apply first on that path. `.env.sample:1` says not to use quotes.

**decouple 3.8** (V:decouple.py):

- Lookup order: `os.environ`, then the file, then `default`; with no default `UndefinedValueError` (`:86-94`).
- File: on the first call, start in the directory of the calling module (`pyUltroid/`), take `settings.ini` if present, else `.env`, else go up one directory; the filesystem root is not searched (`:202-205, 213-226, 238-248`). **run**: the working directory plays no part, and a `settings.ini` hides `.env`.
- `.env` parsing (`:150-160`): read as UTF-8; strip the line; skip it if empty, starting with `#` or without `=`; split at the first `=`; strip key and value; drop one pair of matching outer quotes. Nothing else: no `export`, inline comments, escapes, `$` expansion or multi-line values. A later duplicate replaces an earlier one.
- `cast=bool` (`:30-43, 69-74`): `""` is False; otherwise the lower-cased text must be one of `y yes t true on 1` or `n no f false off 0`; anything else, `" true"` included, raises `ValueError` (**run**).
- `cast=int` is Python `int()`: "preceded by + or -", "leading zeros", "surrounded by whitespace", "single underscores", "any Unicode decimal digit", unbounded (https://docs.python.org/3/library/functions.html#int). `""` raises `ValueError` (**run**).
- The default is cast too (`:94-101`). A bad value is an uncaught exception while `configs.py` is imported. **run** with `.env.sample` copied unchanged: `BOT_TOKEN` is `''`, not `None`; `ADDONS` is False; `API_ID=` and `LOG_CHANNEL=` raise `ValueError`.

**python-dotenv 1.2.4** fills `os.environ` before decouple looks, so its dialect wins for every key it sets. File: from the calling module's directory upward, or the working directory when interactive, frozen or under a debugger (V:dotenv/main.py:337-385). Existing variables are kept (`override=False`, `:104-108, 392`). BOM stripped, `export` accepted, quoted values with escapes and line breaks, inline ` #` comments, `KEY` without `=` not set (V:dotenv/parser.py:21-34, 73, 125-141, 164-169; main.py:107-108). `${NAME}` and `${NAME:-default}` are expanded in every value (V:dotenv/variables.py:5-15; main.py:294-316).

**Candidates.** `dotenvy` 0.15.7, MIT (ci), released 2023-03-22 (io); the repository README describes an unpublished 0.16 (https://github.com/allan2/dotenvy). `dotenv-ng` 1.0.0, MIT (ci), 2026-08-16 (io), "a modernized fork of `dotenvy`" (R:dotenv-ng-1.0.0/README.md). `dotenv` 0.15.0: last release 2019-10-21 (io). `rust-decouple` 0.3.0: "not ready for use", reads only `env::var`, no file (R:rust-decouple-0.3.0/README.md; src/core.rs:27, 47). `decouple` 0.1.0 (2020-12-11, io) contains one `main.rs`.

**Fit: partial** for dotenvy and dotenv-ng (another dialect); **none** for decouple's lookup and casts.

decouple and python-dotenv columns are **run** on lines of these shapes. The dotenvy column is read from R:dotenvy-0.15.7/src/parse.rs (bare line numbers) and src/iter.rs, not run. The dotenv-ng column is its README.

| line in `.env` | decouple 3.8 | python-dotenv 1.2.4 | dotenvy 0.15.7 | dotenv-ng 1.0.0 |
| --- | --- | --- | --- | --- |
| `K=a b` | `a b` | `a b` | error (`:139-150`) | `a b` |
| `K=v # c` | `v # c` | `v` | `v` | `v` |
| `K=#x` | `#x` | `#x` | empty (`:64-67`) | not stated |
| `K=pa$$w0rd$HOME` | unchanged | unchanged | `$NAME` and `${NAME}` substituted, environment first (`:171-217, 260-274`) | unchanged by default |
| `K='x${HOME}y'` | unchanged | expanded | unchanged (`:165-170`) | unchanged by default |
| `K=C:\Users` | unchanged | unchanged | error: only backslash + `\`, `'`, `"`, `$`, space, `n` (`:151-162`) | unchanged |
| `K="a\tb"` | `a\tb` as typed | tab | error (same lines) | tab |
| `K="abc` | `"abc` | skipped with a warning; can swallow following lines | error (`:240-249`; iter.rs:136-141) | not stated |
| `export K=1` | key `export K` | `K` | `K` (`:51-58`) | `K` |
| `K` without `=` | skipped | not set | error (`:96-99`) | not stated |
| `K=1` then `K=2` | `2` | `2` | `1` (iter.rs:27-40) | not stated |
| key characters | anything before `=` | no `=`, `#`, whitespace; or `'..'` | `[A-Za-z_][A-Za-z0-9_.]*` (`:76-94`) | "non-whitespace characters" |
| BOM | stays in the first key | stripped | stripped (iter.rs:58-66) | not stated |
| malformed line | skipped | skipped | loading stops with `Err` (iter.rs:32-37) | not stated |
| file searched from | calling module's directory | calling module's directory | working directory upward (src/find.rs:24-57) | `./.env` only (R:dotenv-ng-core-1.0.0/src/lib.rs:216-218) |

Other traps:
- Rust's integer parser: "an optional `+` or `-` sign followed by only digits. Leading and trailing non-digit characters (including whitespace) represent an error. Underscores ... also represent an error" (https://doc.rust-lang.org/std/primitive.i64.html, `impl FromStr for i64`).
- `update_envs` stores environment text through `set_key`, that is through `literal_eval` (`funcs.py:108-111`; `_database.py:94-99`): `BOTMODE=True` becomes a bool, while `BOTMODE=true` and `BOTMODE=false` stay non-empty strings. `cast=bool` treats the same texts differently.
- `std::env::set_var` is `unsafe`: "In multi-threaded programs on other operating systems, the only sound option is to not use `set_var` or `remove_var` at all" (https://doc.rust-lang.org/std/env/fn.set_var.html). Python sets variables at import time, and again for `TZ` at run time (`funcs.py:150`).

## 7. `pyyaml`

**Use.** `strings/__init__.py:27`: `safe_load(open(file, encoding="UTF-8"))` on `strings/strings/<lang>.yml` (24 files). If PyYAML is missing, a line-based fallback that calls `eval` on each value is used (`strings/__init__.py:9-12`; `pyUltroid/fns/tools.py:1052-1082`). PyYAML is not in `requirements.txt`, `resources/startup/optional-requirements.txt` or `installer.sh`; only CI installs it (`.github/workflows/stringanalysis.yml:21`).

**PyYAML 6.0.3.** "a complete YAML 1.1 parser" (V:pyyaml-6.0.3.dist-info/METADATA). Only plain scalars are resolved (V:yaml/parser.py:328-331; yaml/resolver.py:143-153): bool `yes`, `no`, `true`, `false`, `on`, `off` in three spellings, not `y`/`n`; int with `0b`, `0x`, leading-zero octal, `_`, base 60; float only with a `.`; null `~`, `null`, empty; timestamps; `<<` (V:yaml/resolver.py:170-214; yaml/constructor.py:224-292). A duplicate key silently replaces the earlier one (V:yaml/constructor.py:137-145).

**What the files contain** (**run**: `yaml.compose` on all 24 files): one document each, a block mapping. 11,769 keys, all plain and str. Values: 11,691 double-quoted, 100 plain (all str), 24 block sequences (`authors`). No scalar resolves to bool, int, float, null or timestamp. No duplicate keys, anchors, aliases, tags, flow collections or block scalars. Escapes inside double-quoted values: `\n` 27,102 times, `\"` 6 times, backslash-space 23 times in 14 values (8 files); 3 plain values contain a literal backslash. 69 double-quoted values span lines (10 files), so line folding applies. `uz.yml` has CRLF line ends; 19 files have no final newline.

Each of these prints nothing (bool or null words, numbers, special keys):

```
grep -nEi '^[^"#]*(:|-)[[:space:]]+(y|n|yes|no|on|off|true|false|null|~)[[:space:]]*$' strings/strings/*.yml
grep -nE  '^[^"#]*(:|-)[[:space:]]+[-+.]?[0-9][0-9_:.eExXoObBa-fA-F-]*[[:space:]]*$' strings/strings/*.yml
grep -nEi '^(y|n|yes|no|on|off|true|false|null|~|[-+.]?[0-9][0-9_:.]*)[[:space:]]*:' strings/strings/*.yml
```

This one lists the unquoted values other than `name` and `natively`, 8 lines (`fa.yml:123, 324`, `fr.yml:117`, `uz.yml:108, 194, 223, 321, 326`):

```
grep -nE '^[A-Za-z0-9_]+:[[:space:]]+[^"[:space:]]' strings/strings/*.yml | grep -vE '\.yml:[0-9]+:(name|natively): '
```

**Candidates.**

- `serde_yaml_ng` 0.10.0, MIT (ci), released 2024-05-26 (io), on `unsafe-libyaml`. README: "This library only follows the YAML specification 1.1" (R:serde_yaml_ng-0.10.0/README.md:10); the repository page adds "This is a library for myself, don't expect professional support" (https://github.com/acatton/serde-yaml-ng). Its scalar code is not 1.1: bool only `true`, `false` in three spellings; null `null`, `~` or empty; ints with `0x`, `0o`, `0b`; "Leading zero(s) followed by numeric characters is a string according to the YAML 1.2 spec" (R:serde_yaml_ng-0.10.0/src/de.rs:925-938, 1092-1097, 1127). A duplicate key in a `Mapping` is an error (src/mapping.rs:817-840).
- `saphyr` 0.3.4, MIT OR Apache-2.0 (ci), 2026-11-11 (io): "YAML 1.2 implementation", core schema (R:saphyr-0.3.4/src/lib.rs:5, 53). Bool `true`, `false` in three spellings; null `~`, `null` or empty; `0x`, `0o`; then an `i64` parse, then `f64` (src/scalar.rs:164-167, 180-233). A duplicate key is an error unless `allow_duplicate_keys(true)` (src/loader.rs:277-284, 429-430).
- `yaml_serde` 0.10.7, MIT OR Apache-2.0 (ci), 2026-08-18 (io): "the actively maintained fork of serde-yaml ... by the official YAML organization" (R:yaml_serde-0.10.7/README.md), with the same bool and leading-zero code (src/de.rs:931-937, 1091-1096).
- `serde-saphyr`: ci shows 3.0.0-rc.1, stable is 2.2.0 (io). The target type decides: "if the target field is boolean, serde-saphyr will attempt to interpret standard YAML 1.1 values as boolean"; "Legacy octal notation such as `0052` can be enabled via `Options`, but it is disabled by default" (R:serde-saphyr-3.0.0-rc.1/README.md:724, 743).
- On crates.io, not read: `yaml-rust2` 0.13.1, `serde_norway` 0.9.42 (ci).

The same plain scalar under three parsers (PyYAML column **run**; the others from the code cited above, not run):

| plain scalar | PyYAML 6.0.3 | serde_yaml_ng 0.10.0 | saphyr 0.3.4 |
| --- | --- | --- | --- |
| `yes`, `No`, `on`, `OFF` | bool | string | string |
| `010` | int 8 | string `010` | int 10 |
| `1:30` | int 90 | string | string |
| `1_000` | int 1000 | string | string |
| `0o17` | string | int 15 | int 15 |
| `0b11` | int 3 | int 3 | string |
| `1e3` | string | float | float |
| `~`, `null`, empty | None | null | null |
| `2001-12-14` | `datetime.date` | string | string |

Quoted scalars are strings in all three (R:serde_yaml_ng-0.10.0/src/de.rs:858-904; R:saphyr-0.3.4/src/scalar.rs:139-141).

**Fit: partial.** For the 24 files as they are, the rules above change no value's type, and both scanners decode backslash-space (R:unsafe-libyaml-0.2.11/src/scanner.rs:2240; R:saphyr-parser-0.3.4/src/scanner.rs:2227). No Rust parser was run on the files.

Traps:
- The reference is two parsers. **run**: the fallback agrees with PyYAML on 11,686 of 11,769 keys, differs on 83 (the 69 multi-line values and the 14 with backslash-space) and adds 55 keys made from continuation lines. `en.yml` is identical under both.
- A user-edited file with `on`, `off`, `yes`, `no`, a leading-zero number or a duplicate key loads differently, or not at all (table above; duplicate-key errors).

## 8. `aiohttp`, `requests`

**Use.** Async calls go through `async_searcher` (`pyUltroid/fns/helper.py:380-416`): a new `ClientSession(headers=headers)` per call; `get`, `post` or `head`; pass-through `json=`, `data=`, `headers=`; the result is `text()`, `json(content_type=None)`, `read()` or the response object. `download_file` checks `Content-Type` (`:423-433`); `fast_download` streams with `iter_chunked(1024)`, `ClientTimeout(total=None)` and reads `content-length` (`:436-456`). Direct sessions: `pyUltroid/fns/misc.py:172-182`, `assistant/manager/misc.py:61-63`. `ContentTypeError` is caught at `fns/misc.py:409`. `requests` has one core call, `requests.get(url, timeout=60).content` in `translate` (`pyUltroid/fns/tools.py:712-720`), reached from `strings/__init__.py:45`. No cookies, proxies, client certificates or TLS settings.

**Candidate.** `reqwest` 0.13.5, MIT OR Apache-2.0 (ci), released 2026-09-08 (io).

**Fit: good.** Every call has a counterpart. The defaults differ:

| | aiohttp 3.14.5 (V:aiohttp/) | requests 2.34.2 (V:requests/) | reqwest 0.13.5 (R:reqwest-0.13.5/) |
| --- | --- | --- | --- |
| timeout | total 300 s, socket connect 30 s (client.py:274) | none unless passed (sessions.py:567) | none (src/async_impl/client.rs:1449, 1469) |
| proxy variables | ignored, `trust_env=False` (client.py:355) | used, `trust_env=True` (sessions.py:492) | used: "System proxies are enabled by default" (src/lib.rs:142-156) |
| redirects | 10; `head()` does not follow (client.py:570-571, 1547) | 30 (models.py:104) | 10 (src/lib.rs:131-135) |
| `User-Agent` | `Python/3.11 aiohttp/3.14.5` (http.py:72-74; client_reqrep.py:1307-1308) | `python-requests/2.34.2` (utils.py:942-962) | none; only `Accept: */*` is preset (src/async_impl/client.rs:284-285) |
| compressed bodies | asks for gzip, deflate (br, zstd if installed) and decodes (client_reqrep.py:98-107, 1012-1015; client.py:354) | asks and decodes (utils.py:91, 958; models.py:937) | only with features `gzip`, `deflate`, `brotli`, `zstd`, none on by default (Cargo.toml; src/lib.rs:204-207) |
| trust store | `ssl.create_default_context()`, the system store (connector.py:911) | certifi bundle, or `REQUESTS_CA_BUNDLE` / `CURL_CA_BUNDLE` (certs.py; utils.py:82; sessions.py:857-858) | default feature `rustls` with `rustls-platform-verifier` (Cargo.toml) |

Traps:
- Off by default: `json`, `form`, `multipart`, `stream`, `cookies`, `blocking` (R:reqwest-0.13.5/Cargo.toml; src/lib.rs:187-217). `Response::chunk()` needs no feature, `bytes_stream()` needs `stream` (src/async_impl/response.rs:310, 349-351).
- aiohttp picks the body type from the values in `data=`: a dict holding a file object or `bytes` becomes `multipart/form-data` (bytes get the field name as file name), otherwise it is form-urlencoded (V:aiohttp/formdata.py, `add_field`). This affects `fns/misc.py:171-174`, `fns/tools.py:263, 286` and `fns/tools.py:404-410`. reqwest has separate `form` and `multipart` calls.
- `text()`: aiohttp takes the charset from the header, UTF-8 for JSON, else a resolver (V:aiohttp/client_reqrep.py:918-939). reqwest defaults to UTF-8 and replaces malformed sequences with U+FFFD (R:reqwest-0.13.5/src/async_impl/response.rs:133-141).
- `json()`: aiohttp checks for `application/json` unless `content_type=None` (V:aiohttp/client_reqrep.py:956-965); reqwest only parses (R:reqwest-0.13.5/src/async_impl/response.rs:260-264).

## 9. `apscheduler`

**Use.** `pyUltroid/__main__.py:28-31` imports `AsyncIOScheduler` and does not use it. The uses are in plugins: `add_job(f, "interval", seconds=n)` (`plugins/autopic.py:150-154`) and `add_job(f, trigger="cron", hour=h, minute=m)` twice (`plugins/nightmode.py:147-155`).

**APScheduler 3.11.3** (W:apscheduler 3.11.3/apscheduler/). The scheduler's zone is `tzlocal.get_localzone()` (schedulers/base.py:905), so it follows the `TZ` Ultroid exports from the `TIMEZONE` key (`pyUltroid/startup/funcs.py:146-151`) or the image's `ENV TZ=Asia/Kolkata` (`Dockerfile:9`). Job defaults: `misfire_grace_time` 1 s, `coalesce` True, `max_instances` 1 (base.py:911-913). An interval job first fires one interval after start (triggers/interval.py:15-18, 70). Cron fields below the given ones default to their minimum, so second 0 (triggers/cron/__init__.py:105-115).

**Candidate.** `tokio-cron-scheduler` 0.15.1, MIT/Apache-2.0 (ci), released 2025-10-28 (io).

**Fit: partial.** Both job kinds exist: `Job::new_repeated_async(Duration, ..)` and cron strings in the order `sec min hour day-of-month month day-of-week` (R:tokio-cron-scheduler-0.15.1/src/job/mod.rs:611; README.md:25-30).

Traps:
- "Time is specified for `UTC` and not your local timezone"; the `_tz` constructors take a zone (R:tokio-cron-scheduler-0.15.1/README.md:32-34; src/job/mod.rs:208).
- Late, missed or overlapping runs are not described: a search of the README and of `src/` for misfire, coalesce, overlap and missed finds nothing.

## 10. `pytz`

**Use.** In the core only as a name check: `timezone(TZ)` must not raise, then `os.environ["TZ"] = TZ; time.tzset()` (`pyUltroid/startup/funcs.py:19-21, 146-159`). `assistant/start.py:238` checks user input the same way. Conversions are in plugins (`plugins/weather.py:35-48`; `plugins/specialtools.py:154-166`).

**pytz 2026.6** (W:pytz 2026.6/pytz/__init__.py): bundled database 2026f (`:25`); lookup ignores case, `UTC` in any case, unknown names raise `UnknownTimeZoneError` (`:185-205, 219-224`).

**Candidates.** `jiff` 1.0.1, Unlicense OR MIT (ci), released 2026-11-18 (io). `chrono-tz` 0.10.4, MIT OR Apache-2.0 (ci), 2025-07-11 (io).

**Fit: good** (jiff), **partial** (chrono-tz), for the name check.

- jiff: "The lookup is performed without regard to ASCII case" (R:jiff-1.0.1/src/tz/db/mod.rs:489-492; https://docs.rs/jiff/1.0.1/jiff/tz/struct.TimeZoneDatabase.html). By default it reads the system's database and bundles one only where none exists (R:jiff-1.0.1/src/lib.rs:663-669).
- chrono-tz: exact-match lookup, `TIMEZONES.get(s)` (R:chrono-tz-0.10.4/src/prebuilt/timezones.rs:1946-1951); `case-insensitive` is a feature (ci). Data is compiled in at version 2025b (src/prebuilt/directory.rs:1): 597 names, links such as `US/Eastern` and `Asia/Calcutta` included (timezones.rs:1719, 1747, 75921).

Traps:
- Three databases decide what a valid name is: pytz's own copy, the host's zoneinfo (read by `tzset()` and by jiff) and chrono-tz's compiled copy.
- pytz accepts `asia/kolkata`; Ultroid then exports the text as typed (`funcs.py:149-150`). What `tzset()` does with a wrongly-cased name was not verified.
- Changing `TZ` inside a running multi-threaded process: see `set_var` in section 6.

## 11. `gitpython`

**Use.** Updater (`pyUltroid/fns/helper.py:294-331`): `Repo()`, `remotes[0].config_reader.get("url")`, `head.is_detached`, `active_branch.name`, `create_remote("upstream", url)`, `remote("upstream").fetch(branch)`. Changelog (`:251-267`): `iter_commits("HEAD..upstream/<branch>")` with `c.count()`, `c.committed_datetime`, `c.summary`, `c.author`. For a directory that is not a repository: `Repo.init()`, fetch, create and check out `main` (`:312-318`). `pyUltroid/startup/loader.py:76` reads the branch name. `assistant/callbackstuffs.py:281-318` adds `repo.git.reset("--hard", "FETCH_HEAD")`, `remote.set_url` and `remote.push(refspec=.., force=True)`. The `git` program is also run directly (`loader.py:71-90, 130-136`; `plugins/bot.py:222`).

**GitPython 3.2.1** (V:git/). "GitPython needs the `git` executable to be installed" (V:gitpython-3.2.1.dist-info/METADATA:92-94). Fetch, push, `rev-list` and `Commit.count()` are `git` subprocesses (remote.py:1085, 1223; objects/commit.py:297-298, 367), so the user's git configuration applies. `Repo()` uses `GIT_DIR` or the working directory and does not search parents (repo/base.py:233, 278-284). `remotes` follows the order of the config file (remote.py:632-641).

**Candidates.** `git2` 0.21.0, MIT OR Apache-2.0 (ci), released 2026-05-18 (io). `gix` 0.90.0, MIT OR Apache-2.0 (ci), 2026-10-22 (io).

**Fit: partial** for both.

- `git2`: the calls exist: `Repository::open` (that path only) and `discover`, `find_remote`, `remote`, `remote_set_url`, `reset`, `head_detached`, `revwalk` with `push_range`, `Remote::{url, fetch, push}`, `Commit::{summary, time, author}` (R:git2-0.21.0/src/repo.rs:131-133, 246-249, 611, 622, 740, 782, 869, 2532; src/revwalk.rs:129; src/remote.rs:146, 325, 370; src/commit.rs:130, 177, 203). Traps: `default = []`, with `https` and `ssh` as opt-in features (Cargo.toml; ci). Credentials come from a callback; `Cred::credential_helper` reads `credential.helper` only when called (src/cred.rs:113-122). The crate describes itself as "likely lacking some bindings here and there" (src/lib.rs:4-5).
- `gix`: the status file marks clone, fetch, rev-walk and credential helpers done, and `push`, "checkout, switch, restore and reset", remotes "save to configuration on disk" and "write `FETCH_HEAD`" not done (https://raw.githubusercontent.com/GitoxideLabs/gitoxide/main/crate-status.md). The network clients are not among the default features (R:gix-0.90.0/Cargo.toml, `[features] default`).

## 12. `heroku3`

**Use.** `heroku3.from_key(key)`, then `.app(name)` or `.apps()[name]`; `app.get_log()` (`pyUltroid/fns/helper.py:206-236`); `app.restart()` (`:595-609`); `app.process_formation()[type].scale(0)` (`:628-645`); `apps()`, `app.name`, `app.git_url` (`assistant/callbackstuffs.py:286-313`); `account().id` (`plugins/usage.py:112`).

**heroku3 5.2.1** (released 2023-04-17, https://pypi.org/pypi/heroku3/json) is `requests` calls to `https://api.heroku.com` with `Accept: application/vnd.heroku+json; version=3.cedar-acm`, HTTP Basic auth with an empty user name and the key as password, and `trust_env = False` (W:heroku3 5.2.1/heroku3/api.py:42-43, 81; core.py:22-24). `from_key` sends `GET /account/rate-limits` and records the outcome without raising (api.py:76-97). `restart()` lists the dynos and sends `DELETE /apps/{id}/dynos/{name}` for each one whose type is not `run` (models/app.py:273-277; models/dyno.py:25-30). `get_log()` posts `{"lines": 100}` to `/apps/{id}/log-sessions` and fetches the URL it gets back (models/app.py:502-524). `scale(0)` reads `/apps/{name}/formation` and sends `PATCH /apps/{id}/formation/{type}` with `{"quantity": 0}` (models/app.py:309-311; models/formation.py:27-49). `apps()[name]` downloads the whole app list first (api.py:340-341).

**Candidates.** `heroku_rs` 0.6.0, MIT OR Apache-2.0 (ci), last release 2021-05-29 (io); `herokuru` 0.1.1, licence "unknown" (ci), last release 2021-06-09 (io).

**Fit: none.** No crate has been released since 2021. The service is plain REST: base URL `https://api.heroku.com`, `Accept: application/vnd.heroku+json; version=3`, `Authorization: Bearer <token>` (https://devcenter.heroku.com/articles/platform-api-reference, first 100,000 characters read).

Trap: heroku3 switches the proxy variables off; reqwest has them on (section 8).

## 13. `coloredlogs` and the `logging` setup

**Use** (`pyUltroid/startup/__init__.py:49-81`):

- File: `ultroid.log`, or `ultroid<n>.log` when a seventh argument is given (`:49`; `multi_client.py:23` passes the client number). An existing file is deleted at start (`:51-52`), then opened in append mode with the locale's encoding (`FileHandler(file)`, `:73`; CPython 3.11 `Lib/logging/__init__.py:1156-1168`).
- Line: `%(asctime)s | %(name)s [%(levelname)s] : %(message)s` with `datefmt="%m/%d/%Y, %H:%M:%S"`, level INFO, written to the file and to stderr by handlers on the root logger (`:68-74`). Shape: `11/20/2026, 19:17:01 | pyUltLogs [INFO] : Python version - 3.11.18`.
- The time is local time (`converter = time.localtime`, `logging/__init__.py:574`) and follows `TZ`.
- Logger names: `pyUltLogs` (`:55`) and `Telethon` with its children, set to INFO and handed to the client as `base_logger` (`:56-57`; `pyUltroid/startup/BaseClient.py:50`). Level names: `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG` (`logging/__init__.py:101-108`). A record can span lines: the start-up banner (`:83-89`) and tracebacks (`logging/__init__.py:694-699`).
- Readers (`plugins/bot.py:238-275`): `.logs` sends the file; `.logs open` the last 4,000 characters; `.logs <5..100>` the last N lines; `.logs carbon` the last 2,500 characters.
- `coloredlogs` is optional (`:75-81`); only the Termux installer installs it (`resources/startup/_termux.py:245`). In 15.0.1, `install(level=None, logger=LOGS, fmt=..)` removes the stderr handler it finds up the logger tree, here the root one, and adds its own to that logger, with `datefmt` `%Y-%m-%d %H:%M:%S` unless given, level INFO, colours only on a terminal and without `NO_COLOR` (W:coloredlogs 15.0.1/coloredlogs/__init__.py:219, 225, 313 ff., 842-865). With coloredlogs the console shows another date format than the file; the file is unaffected.

**Candidates.** `log` 0.4.35, MIT OR Apache-2.0, with `fern` 0.7.1, MIT (ci). Colour: `owo-colors` 4.4.0, `anstream` 1.0.0 (ci; `rust/PLAN.md:130`). On crates.io, not read: `tracing` 0.1.44, `tracing-subscriber` 0.3.23, `tracing-appender` 0.2.5, `flexi_logger` 0.32.0 (ci).

**Fit: partial.** `fern` takes a format closure and chains stdout and `fern::log_file(..)` (R:fern-0.7.1/src/lib.rs:26-52); the line above has to be written in that closure.

Traps:
- `log` has `ERROR`, `WARN`, `INFO`, `DEBUG`, `TRACE` (R:log-0.4.35/src/lib.rs:468): no `CRITICAL`, and `WARN` where Python writes `WARNING`.
- `fern::log_file` opens with create and append (R:fern-0.7.1/src/lib.rs:318-326); Ultroid deletes the previous file first.
- The Telethon lines come from the Telegram library (ADR-005).

## 14. `psutil`, `certifi`

**psutil.** Not imported by the core. `plugins/usage.py:71-82` calls `cpu_percent()`, `virtual_memory().percent`, `disk_usage("/").percent`, `net_io_counters().bytes_sent` and `.bytes_recv`.

- psutil 7.2.2 (W:psutil 7.2.2/psutil/): `cpu_percent()` without an interval returns at once, the first time "a meaningless 0.0 value" (__init__.py:1788-1798). Memory percent is `(total - available) / total` to one decimal (_pslinux.py:410). Disk percent is `used / (used + free for the user)` to one decimal (_psposix.py:336-340). Network counters are system-wide totals (__init__.py:2152-2181).
- Candidates: `sysinfo` 0.40.4, MIT (ci), released 2026-11-16 (io). `psutil` 5.4.0, MIT, 2025-07-25 (ci, io), not read.
- **Fit: partial.** sysinfo returns bytes, not percentages (R:sysinfo-0.40.4/src/common/system.rs:614-625). Its CPU figure "is based on diff" and needs two refreshes at least `MINIMUM_CPU_UPDATE_INTERVAL` (200 ms) apart (`:178, 568-585`). The percentages and rounding above have to be computed by the caller.

**certifi.** Imported at `pyUltroid/fns/tools.py:27-30` and not used: `grep -rn certifi --include=*.py .` finds only those lines. `ssl` (`:15`) is unused too. The trust stores in use are those in the section 8 table: the system store for aiohttp, and for `requests` the certifi bundle ("Mozilla's carefully curated collection of Root Certificates", V:certifi-2026.10.23.dist-info/METADATA).

- `webpki-roots` 1.0.12, CDLA-Permissive-2.0: "Mozilla's CA root certificates for use with webpki" (ci), the compiled-in counterpart of certifi. `rustls-native-certs` 0.8.5, Apache-2.0 OR ISC OR MIT (ci): the platform store, honouring `SSL_CERT_FILE` and `SSL_CERT_DIR`; its README suggests `rustls-platform-verifier` (0.7.1, ci) instead (R:rustls-native-certs-0.8.5/README.md; src/lib.rs:52-53). reqwest 0.13.5 uses the platform verifier by default (section 8).
- **Fit: good**, nothing in the core to replace. Trap: the one `requests` call (`fns/tools.py:720`) would move from the certifi bundle to the platform store, and `REQUESTS_CA_BUNDLE` / `CURL_CA_BUNDLE` would no longer be read.

## Summary table

| Dependency | Candidate | Fit | Biggest trap |
| --- | --- | --- | --- |
| `redis` | `redis` 1.8.2 (ci shows 2.0.0-rc.3) | good | `REDIS_URI` is `host:port`, not a URL the crate parses; 500 ms default timeout |
| `pymongo` | `mongodb` 3.10.2 | good | 30 s server selection; compiled-in CA roots instead of the system store |
| `psycopg2` | `tokio-postgres` 0.7.18, `sqlx` 0.9.1 | partial | one unquoted column per key: lower-cased names, column limit, string returned after a write |
| `localdb.json` | none (`serde_json` 1.0.154 for one variant) | none | file is a Python dict `repr` (PyPI 1.0) or JSON (repository main); deletes not written |
| stored value format | `py_literal` 0.4.0, `rustpython-literal` 0.6.0 | partial | `007`, `2021-12-25`, `1+2` read as numbers; printing is not `repr()` |
| `python-decouple`, `python-dotenv` | `dotenvy` 0.15.7, `dotenv-ng` 1.0.0 | partial | another dialect, errors where Python accepts; an empty value is not unset |
| `pyyaml` | `serde_yaml_ng` 0.10.0, `saphyr` 0.3.4 | partial | reference is PyYAML or the fallback (83 keys differ); YAML 1.1 scalars resolve differently |
| `aiohttp`, `requests` | `reqwest` 0.13.5 | good | proxy variables on, no `User-Agent`, no timeout, decompression off |
| `apscheduler` | `tokio-cron-scheduler` 0.15.1 | partial | cron in UTC unless a zone is passed; missed-run rules undocumented |
| `pytz` | `jiff` 1.0.1; `chrono-tz` 0.10.4 | good; partial | three tz databases; chrono-tz is case-sensitive and compiled at 2025b |
| `gitpython` | `git2` 0.21.0; `gix` 0.90.0 | partial | GitPython runs `git` with the user's configuration; https and ssh off by default; gix has no push or reset |
| `heroku3` | none maintained; REST over `reqwest` | none | restart is one DELETE per dyno; Basic auth; proxy variables ignored |
| `logging`, `coloredlogs` | `log` 0.4.35 with `fern` 0.7.1 | partial | level names `WARNING` and `CRITICAL`; file deleted at start; date format |
| `psutil` | `sysinfo` 0.40.4 | partial | percentages and rounding are psutil's own arithmetic |
| `certifi` | not needed (`webpki-roots` 1.0.12 is the counterpart) | good | unused import; `requests` trusts the certifi bundle today |

## Not verified

- No Rust crate was compiled or run. The `py_literal` results for `007`, `2021-12-25` and `1+2`, every dotenvy cell of the section 6 table and the serde_yaml_ng and saphyr columns of the section 7 table are read from source. No Rust YAML parser was run on the 24 language files (line folding, backslash-space, CRLF, missing final newline).
- What deployed environments contain: whether the image `theteamultroid/ultroid:main` (`Dockerfile:6`) has PyYAML or coloredlogs, and which redis-py, pymongo, psycopg2 and localdb builds are installed. The image was not inspected.
- PostgreSQL: that repeated drop and add of a column really exhausts the 1,600-column limit was taken from the limits page, not tested.
- `rustpython-literal`: which Unicode version `is_repr_printable` uses, and whether `float::to_string` equals `repr(float)` beyond its own tests. The crate has no documentation.
- `rustpython-parser`, `ruff_python_parser`: which Python grammar version they implement, and whether their ASTs carry everything `literal_eval` needs. Only the READMEs and the leading-zero check were read.
- `dotenv-ng`: only the README and the loader defaults were read; the cells marked "not stated". `serde-saphyr`: only the 3.0.0-rc.1 README, not 2.2.0. `yaml_serde`: only two functions. `yaml-rust2`, `serde_norway`: not read.
- `redis` 2.0.0-rc.3 was not read; all redis claims are for 1.8.2. Whether the crate's sync connection has default timeouts was not checked.
- `mongodb`: the BSON number type the driver returns for `dbstats.dataSize`.
- `sqlx`: only the connection-option files of `sqlx-postgres`; its TLS features and behaviour with one DDL statement per key were not examined.
- `tokio-cron-scheduler`: behaviour on late, missed or overlapping runs (no mention found; the scheduling code was not read).
- `git2`, `gix`: the order of the remotes list compared with GitPython's config-file order (`helper.py:255, 298` use `remotes[0]`). For gix only the status file and the manifest were read.
- Heroku: the dyno, formation and log-session sections of the Platform API reference were beyond the part of the page that was read; the endpoints listed come from heroku3's source.
- Logging: `tracing`, `tracing-subscriber`, `tracing-appender` and `flexi_logger` were not read. `sysinfo`: disk and network API not read.
- PyYAML's "YAML 1.1" statement is from the package metadata; https://pyyaml.org/wiki/PyYAMLDocumentation does not state a version.
- `time.tzset()` with a wrongly-cased zone name (section 10).
