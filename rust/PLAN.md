# Rust migration plan: Ultroid (Python)

1 packages, 155 source files (24388 lines), 0 test files, 0 UI files, grouped into 12 units.

| Ready | Caution | Blocked | Keep in source language |
| ---: | ---: | ---: | ---: |
| 5 | 5 | 2 | 0 |

## Start here

Best first ports: safe to port (readiness) and worth porting (loops and string work, tests, size).

| # | Unit | Lines | Priority | Readiness | Tests | Bridge | Main risks |
| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | `strings/` | 68 | 59 | 77 | 0 | PyO3 | String offsets and slicing (2); Runtime changes to code (1); Dynamic typing (2) |
| 2 | `resources/startup/` | 331 | 56 | 87 | 0 | PyO3 | Dynamic typing (3); Exceptions (1) |
| 3 | `resources/session/` | 152 | 55 | 84 | 0 | PyO3 | Dynamic typing (1); Exceptions (7) |
| 4 | `pyUltroid/dB/` | 616 | 37 | 61 | 0 | PyO3 | Dynamic typing (83); Exceptions (5) |

### `strings/`

68 lines in 1 files, wave 0, priority 59, readiness 77, bridge **PyO3**.

- Import cycle with pyUltroid/startup/, pyUltroid/dB/, pyUltroid/_misc/, pyUltroid/fns/, pyUltroid/: port them together.
- No tests found: write characterization tests against the original code first.
- String offsets and slicing x2: `strings/__init__.py:25`, `strings/__init__.py:31`
- Runtime changes to code x1: `strings/__init__.py:14`
- Dynamic typing x2: `strings/__init__.py:20`, `strings/__init__.py:66`
- Exceptions x4: `strings/__init__.py:9`, `strings/__init__.py:26`, `strings/__init__.py:40`

### `resources/startup/`

331 lines in 2 files, wave 0, priority 56, readiness 87, bridge **PyO3**.

- Leaf: imports no other unit.
- No tests found: write characterization tests against the original code first.
- Dynamic typing x3: `resources/startup/_termux.py:86`, `resources/startup/_termux.py:93`, `resources/startup/locals.py:96`
- Exceptions x1: `resources/startup/locals.py:110`

### `resources/session/`

152 lines in 1 files, wave 0, priority 55, readiness 84, bridge **PyO3**.

- 2 PyPI dependencies not in the crate table: check them by hand.
- Leaf: imports no other unit.
- No tests found: write characterization tests against the original code first.
- Dynamic typing x1: `resources/session/ssgen.py:23`
- Exceptions x7: `resources/session/ssgen.py:47`, `resources/session/ssgen.py:57`, `resources/session/ssgen.py:83`

### `pyUltroid/dB/`

616 lines in 21 files, wave 0, priority 37, readiness 61, bridge **PyO3**.

- Import cycle with pyUltroid/startup/, strings/, pyUltroid/_misc/, pyUltroid/fns/, pyUltroid/: port them together.
- No tests found: write characterization tests against the original code first.
- Dynamic typing x83: `pyUltroid/dB/afk_db.py:17`, `pyUltroid/dB/antiflood_db.py:16`, `pyUltroid/dB/antiflood_db.py:22`
- Exceptions x5: `pyUltroid/dB/__init__.py:6`, `pyUltroid/dB/forcesub_db.py:31`, `pyUltroid/dB/warn_db.py:17`

## Order by package

Packages come after the workspace packages they use. Inside a package, port by wave: a unit's imports are in earlier waves.

### 1. root (`.`, portable, 0 test files)

| Wave | Unit | Status | Lines | Readiness | Bridge | Main risks |
| ---: | --- | --- | ---: | ---: | --- | --- |
| 0 | `multi_client.py` | ready | 24 | 97 | PyO3 | Dynamic typing (1) |
| 0 | `resources/startup/` | ready | 331 | 87 | PyO3 | Dynamic typing (3); Exceptions (1) |
| 0 | `resources/session/` | ready | 152 | 84 | PyO3 | Dynamic typing (1); Exceptions (7) |
| 0 | `strings/` | ready | 68 | 77 | PyO3 | String offsets and slicing (2); Runtime changes to code (1) |
| 0 | `pyUltroid/dB/` | ready | 616 | 61 | PyO3 | Dynamic typing (83); Exceptions (5) |
| 0 | `pyUltroid/` | caution | 309 | 58 | PyO3 | Class inheritance (3); Exceptions (5) |
| 0 | `pyUltroid/_misc/` | caution | 664 | 31 | PyO3 | String offsets and slicing (2); Regexes built at runtime (2) |
| 0 | `pyUltroid/fns/` | blocked | 3089 | 0 | PyO3 | String offsets and slicing (23); Regexes built at runtime (3) |
| 0 | `pyUltroid/startup/` | caution | 1425 | 0 | PyO3 | String offsets and slicing (3); Runtime changes to code (2) |
| 1 | `plugins/` | blocked | 14394 | 0 | PyO3 | String offsets and slicing (66); Regexes built at runtime (9) |
| 2 | `assistant/` | caution | 2821 | 0 | PyO3 | String offsets and slicing (33); Runtime changes to code (1) |
| 3 | `assistant/manager/` | caution | 495 | 50 | PyO3 | String offsets and slicing (2); Async and promises (151) |

## PyPI dependencies

| Package | Units | Rust | Fit | Note |
| --- | ---: | --- | --- | --- |
| `telethon` | 7 | ? | unknown |  |
| `catbox` | 3 | ? | unknown |  |
| `git` | 3 | ? | unknown |  |
| `heroku3` | 3 | ? | unknown |  |
| `pytz` | 3 | ? | unknown |  |
| `apscheduler` | 2 | ? | unknown |  |
| `cv2` | 2 | ? | unknown |  |
| `decouple` | 2 | ? | unknown |  |
| `telethonpatch` | 2 | ? | unknown |  |
| `akipy` | 1 | ? | unknown |  |
| `apiclient` | 1 | ? | unknown |  |
| `black` | 1 | ? | unknown |  |
| `certifi` | 1 | ? | unknown |  |
| `cloudscraper` | 1 | ? | unknown |  |
| `coloredlogs` | 1 | ? | unknown |  |
| `dotenv` | 1 | ? | unknown |  |
| `glitch-me` | 1 | ? | unknown |  |
| `googleapiclient` | 1 | ? | unknown |  |
| `htmlwebshot` | 1 | ? | unknown |  |
| `httplib2` | 1 | ? | unknown |  |
| `img2html` | 1 | ? | unknown |  |
| `localdb` | 1 | ? | unknown |  |
| `oauth2client` | 1 | ? | unknown |  |
| `playwright` | 1 | ? | unknown |  |
| `profanitydetector` | 1 | ? | unknown |  |
| `psutil` | 1 | ? | unknown |  |
| `pymongo` | 1 | ? | unknown |  |
| `pypdf2` | 1 | ? | unknown |  |
| `pyrogram` | 1 | ? | unknown |  |
| `pytgcalls` | 1 | ? | unknown |  |
| `qrcode` | 1 | ? | unknown |  |
| `redis` | 1 | ? | unknown |  |
| `safety` | 1 | ? | unknown |  |
| `skimage` | 1 | ? | unknown |  |
| `tabulate` | 1 | ? | unknown |  |
| `telegraph` | 1 | ? | unknown |  |
| `twikit` | 1 | ? | unknown |  |
| `youtubesearchpython` | 1 | ? | unknown |  |
| `yt-dlp` | 1 | ? | unknown |  |
| `bs4` | 3 | quick-xml, scraper | partial |  |
| `pil` | 3 | image | partial |  |
| `numpy` | 2 | ndarray | partial | Broadcasting and dtype rules differ; check numerics. |
| `yaml` | 2 | serde_yaml_ng, saphyr | partial | Round-tripping comments is not covered. |
| `psycopg2` | 1 | sqlx | partial | ORM layers port by hand. |
| `aiohttp` | 3 | reqwest | good |  |
| `requests` | 2 | reqwest | good |  |
| `colorama` | 1 | owo-colors, anstream | good |  |

## Blocked

- `plugins/`: Uses dynamic code (eval, new Function or computed imports).
- `pyUltroid/fns/`: Uses dynamic code (eval, new Function or computed imports).

## Risk guide

- **String offsets and slicing** (High): JS indexes strings in UTF-16 code units, Rust in UTF-8 bytes. Offsets that cross the boundary must be converted, or non-ASCII text gets wrong ranges silently.
- **Regexes built at runtime** (High): Patterns come from data or config in JS syntax. Rust regex syntax differs, so user-visible behavior can change. Pin it with tests on real patterns.
- **Dynamic code (eval, new Function, computed import)** (High): eval, new Function and computed imports have no Rust equivalent. Keep this part in JS or replace it with an explicit registry.
- **Dynamic typing** (Medium): Values whose shape is checked at runtime need an explicit Rust enum or `serde_json::Value`.
- **Exceptions** (Low): Thrown errors become `Result`. Errors crossing the bridge must map back to the same JS error shape.
- **Async and promises** (Medium): Promises become futures. Bridge with napi-rs `async fn` or `wasm-bindgen-futures`, or keep the async shell in JS and port the sync core.
- **Generators** (Medium): Lazy generators become iterators, or return a collected Vec across the bridge.
- **Class inheritance** (Medium): Class hierarchies become traits plus composition; `instanceof` checks become enums.
- **Reflection and prototypes** (Medium): Proxy, Reflect, Symbol and prototype tricks need a redesign, not a translation.
- **Integer width and overflow** (Medium): Python ints never overflow; C, Go and Java ints wrap or are undefined on overflow. Pick i64, i128 or a bignum crate deliberately, and use wrapping_* where the source wraps.
- **Division and modulo** (Medium): Python `//` and `%` floor toward negative infinity; Rust `/` and `%` truncate: use `div_euclid`/`rem_euclid` or explicit floor math. C division by zero is undefined.
- **Hash iteration order** (High): Set and map iteration order comes from the source language's hash function. A port cannot reproduce it: sort before output, or make the order part of the contract.
- **Concurrency** (Medium): Threads, goroutines and locks need a design in Rust (channels, Send/Sync), not a line-by-line translation; keep concurrency in the caller where possible.
- **Runtime changes to code** (High): Code that rewrites classes or modules at runtime has no Rust equivalent: keep it in the source language and port the stable parts.

## Whole app

Shape: **cli**.

| Entry point | Kind | Found from |
| --- | --- | --- |
| `pyUltroid/__main__.py` | cli | `if __name__ == "__main__"` at pyUltroid/__main__.py:104 |

### Every dependency

| Dependency | Declared | Used by | Rust | Fit | Note |
| --- | --- | --- | --- | --- | --- |
| `telethon` | yes | 7 | ? | unknown |  |
| `catbox` | no | 3 | ? | unknown |  |
| `git` | no | 3 | ? | unknown |  |
| `heroku3` | no | 3 | ? | unknown |  |
| `pytz` | no | 3 | ? | unknown |  |
| `apscheduler` | no | 2 | ? | unknown |  |
| `cv2` | no | 2 | ? | unknown |  |
| `decouple` | no | 2 | ? | unknown |  |
| `telethonpatch` | no | 2 | ? | unknown |  |
| `akipy` | no | 1 | ? | unknown |  |
| `apiclient` | no | 1 | ? | unknown |  |
| `black` | no | 1 | ? | unknown |  |
| `certifi` | no | 1 | ? | unknown |  |
| `cloudscraper` | yes | 1 | ? | unknown |  |
| `coloredlogs` | no | 1 | ? | unknown |  |
| `dotenv` | no | 1 | ? | unknown |  |
| `glitch-me` | no | 1 | ? | unknown |  |
| `googleapiclient` | no | 1 | ? | unknown |  |
| `htmlwebshot` | no | 1 | ? | unknown |  |
| `httplib2` | no | 1 | ? | unknown |  |
| `img2html` | no | 1 | ? | unknown |  |
| `localdb` | no | 1 | ? | unknown |  |
| `oauth2client` | no | 1 | ? | unknown |  |
| `playwright` | no | 1 | ? | unknown |  |
| `profanitydetector` | no | 1 | ? | unknown |  |
| `psutil` | no | 1 | ? | unknown |  |
| `pymongo` | no | 1 | ? | unknown |  |
| `pypdf2` | no | 1 | ? | unknown |  |
| `pyrogram` | no | 1 | ? | unknown |  |
| `pytgcalls` | no | 1 | ? | unknown |  |
| `qrcode` | no | 1 | ? | unknown |  |
| `redis` | no | 1 | ? | unknown |  |
| `safety` | no | 1 | ? | unknown |  |
| `skimage` | no | 1 | ? | unknown |  |
| `tabulate` | no | 1 | ? | unknown |  |
| `telegraph` | yes | 1 | ? | unknown |  |
| `twikit` | no | 1 | ? | unknown |  |
| `youtubesearchpython` | no | 1 | ? | unknown |  |
| `yt-dlp` | no | 1 | ? | unknown |  |
| `catbox-uploader` | yes | 0 | ? | unknown |  |
| `enhancer` | yes | 0 | ? | unknown |  |
| `gitpython` | yes | 0 | ? | unknown |  |
| `https` | yes | 0 | ? | unknown |  |
| `python-decouple` | yes | 0 | ? | unknown |  |
| `python-dotenv` | yes | 0 | ? | unknown |  |
| `bs4` | no | 3 | quick-xml, scraper | partial |  |
| `pil` | no | 3 | image | partial |  |
| `numpy` | no | 2 | ndarray | partial | Broadcasting and dtype rules differ; check numerics. |
| `yaml` | no | 2 | serde_yaml_ng, saphyr | partial | Round-tripping comments is not covered. |
| `psycopg2` | no | 1 | sqlx | partial | ORM layers port by hand. |
| `aiohttp` | yes | 3 | reqwest | good |  |
| `requests` | yes | 2 | reqwest | good |  |
| `colorama` | no | 1 | owo-colors, anstream | good |  |

### Pieces, in port order

- wave 0: `multi_client.py` (24 lines)
- wave 0: `pyUltroid/`, `pyUltroid/_misc/`, `pyUltroid/dB/`, `pyUltroid/fns/`, `pyUltroid/startup/`, `strings/`, tangled: one piece (6171 lines)
- wave 0: `resources/session/` (152 lines)
- wave 0: `resources/startup/` (331 lines)
- wave 1: `plugins/` (14394 lines)
- wave 2: `assistant/` (2821 lines)
- wave 3: `assistant/manager/` (495 lines)

### Decisions for the user

**D1** (shape): The app is a cli, entered through pyUltroid/__main__.py. Port every entry point, in that shape?

> Yes: a clap front door (`app front-door`) takes every command over first

**D2** (blocked plugins/): plugins/ is blocked: Uses dynamic code (eval, new Function or computed imports). Rework that part in Rust, or keep the unit outside?

> Research the blocker first; then port it with the piece that uses it

**D3** (blocked pyUltroid/fns/): pyUltroid/fns/ is blocked: Uses dynamic code (eval, new Function or computed imports). Rework that part in Rust, or keep the unit outside?

> Research the blocker first; then port it with the piece that uses it

**D4** (dependency telethon): Which crate replaces telethon (used by 7 units)?

> Research it against primary sources into rust/research/telethon.md before porting what uses it

**D5** (dependency catbox): Which crate replaces catbox (used by 3 units)?

> Research it against primary sources into rust/research/catbox.md before porting what uses it

**D6** (dependency git): Which crate replaces git (used by 3 units)?

> Research it against primary sources into rust/research/git.md before porting what uses it

**D7** (dependency heroku3): Which crate replaces heroku3 (used by 3 units)?

> Research it against primary sources into rust/research/heroku3.md before porting what uses it

**D8** (dependency pytz): Which crate replaces pytz (used by 3 units)?

> Research it against primary sources into rust/research/pytz.md before porting what uses it

**D9** (dependency apscheduler): Which crate replaces apscheduler (used by 2 units)?

> Research it against primary sources into rust/research/apscheduler.md before porting what uses it

**D10** (dependency cv2): Which crate replaces cv2 (used by 2 units)?

> Research it against primary sources into rust/research/cv2.md before porting what uses it

**D11** (dependency decouple): Which crate replaces decouple (used by 2 units)?

> Research it against primary sources into rust/research/decouple.md before porting what uses it

**D12** (dependency telethonpatch): Which crate replaces telethonpatch (used by 2 units)?

> Research it against primary sources into rust/research/telethonpatch.md before porting what uses it

**D13** (dependency akipy): Which crate replaces akipy (used by 1 unit)?

> Research it against primary sources into rust/research/akipy.md before porting what uses it

**D14** (dependency apiclient): Which crate replaces apiclient (used by 1 unit)?

> Research it against primary sources into rust/research/apiclient.md before porting what uses it

**D15** (dependency black): Which crate replaces black (used by 1 unit)?

> Research it against primary sources into rust/research/black.md before porting what uses it

**D16** (dependency certifi): Which crate replaces certifi (used by 1 unit)?

> Research it against primary sources into rust/research/certifi.md before porting what uses it

**D17** (dependency cloudscraper): Which crate replaces cloudscraper (used by 1 unit)?

> Research it against primary sources into rust/research/cloudscraper.md before porting what uses it

**D18** (dependency coloredlogs): Which crate replaces coloredlogs (used by 1 unit)?

> Research it against primary sources into rust/research/coloredlogs.md before porting what uses it

**D19** (dependency dotenv): Which crate replaces dotenv (used by 1 unit)?

> Research it against primary sources into rust/research/dotenv.md before porting what uses it

**D20** (dependency glitch-me): Which crate replaces glitch-me (used by 1 unit)?

> Research it against primary sources into rust/research/glitch-me.md before porting what uses it

**D21** (dependency googleapiclient): Which crate replaces googleapiclient (used by 1 unit)?

> Research it against primary sources into rust/research/googleapiclient.md before porting what uses it

**D22** (dependency htmlwebshot): Which crate replaces htmlwebshot (used by 1 unit)?

> Research it against primary sources into rust/research/htmlwebshot.md before porting what uses it

**D23** (dependency httplib2): Which crate replaces httplib2 (used by 1 unit)?

> Research it against primary sources into rust/research/httplib2.md before porting what uses it

**D24** (dependency img2html): Which crate replaces img2html (used by 1 unit)?

> Research it against primary sources into rust/research/img2html.md before porting what uses it

**D25** (dependency localdb): Which crate replaces localdb (used by 1 unit)?

> Research it against primary sources into rust/research/localdb.md before porting what uses it

**D26** (dependency oauth2client): Which crate replaces oauth2client (used by 1 unit)?

> Research it against primary sources into rust/research/oauth2client.md before porting what uses it

**D27** (dependency playwright): Which crate replaces playwright (used by 1 unit)?

> Research it against primary sources into rust/research/playwright.md before porting what uses it

**D28** (dependency profanitydetector): Which crate replaces profanitydetector (used by 1 unit)?

> Research it against primary sources into rust/research/profanitydetector.md before porting what uses it

**D29** (dependency psutil): Which crate replaces psutil (used by 1 unit)?

> Research it against primary sources into rust/research/psutil.md before porting what uses it

**D30** (dependency pymongo): Which crate replaces pymongo (used by 1 unit)?

> Research it against primary sources into rust/research/pymongo.md before porting what uses it

**D31** (dependency pypdf2): Which crate replaces pypdf2 (used by 1 unit)?

> Research it against primary sources into rust/research/pypdf2.md before porting what uses it

**D32** (dependency pyrogram): Which crate replaces pyrogram (used by 1 unit)?

> Research it against primary sources into rust/research/pyrogram.md before porting what uses it

**D33** (dependency pytgcalls): Which crate replaces pytgcalls (used by 1 unit)?

> Research it against primary sources into rust/research/pytgcalls.md before porting what uses it

**D34** (dependency qrcode): Which crate replaces qrcode (used by 1 unit)?

> Research it against primary sources into rust/research/qrcode.md before porting what uses it

**D35** (dependency redis): Which crate replaces redis (used by 1 unit)?

> Research it against primary sources into rust/research/redis.md before porting what uses it

**D36** (dependency safety): Which crate replaces safety (used by 1 unit)?

> Research it against primary sources into rust/research/safety.md before porting what uses it

**D37** (dependency skimage): Which crate replaces skimage (used by 1 unit)?

> Research it against primary sources into rust/research/skimage.md before porting what uses it

**D38** (dependency tabulate): Which crate replaces tabulate (used by 1 unit)?

> Research it against primary sources into rust/research/tabulate.md before porting what uses it

**D39** (dependency telegraph): Which crate replaces telegraph (used by 1 unit)?

> Research it against primary sources into rust/research/telegraph.md before porting what uses it

**D40** (dependency twikit): Which crate replaces twikit (used by 1 unit)?

> Research it against primary sources into rust/research/twikit.md before porting what uses it

**D41** (dependency youtubesearchpython): Which crate replaces youtubesearchpython (used by 1 unit)?

> Research it against primary sources into rust/research/youtubesearchpython.md before porting what uses it

**D42** (dependency yt-dlp): Which crate replaces yt-dlp (used by 1 unit)?

> Research it against primary sources into rust/research/yt-dlp.md before porting what uses it

**D43** (dependency catbox-uploader): Which crate replaces catbox-uploader (declared, no unit imports it)?

> Research it against primary sources into rust/research/catbox-uploader.md before porting what uses it

**D44** (dependency enhancer): Which crate replaces enhancer (declared, no unit imports it)?

> Research it against primary sources into rust/research/enhancer.md before porting what uses it

**D45** (dependency gitpython): Which crate replaces gitpython (declared, no unit imports it)?

> Research it against primary sources into rust/research/gitpython.md before porting what uses it

**D46** (dependency https): Which crate replaces https (declared, no unit imports it)?

> Research it against primary sources into rust/research/https.md before porting what uses it

**D47** (dependency python-decouple): Which crate replaces python-decouple (declared, no unit imports it)?

> Research it against primary sources into rust/research/python-decouple.md before porting what uses it

**D48** (dependency python-dotenv): Which crate replaces python-dotenv (declared, no unit imports it)?

> Research it against primary sources into rust/research/python-dotenv.md before porting what uses it

**D49** (dependency bs4): bs4 maps to quick-xml, scraper only in part (used by 3 units). Use it?

> Use quick-xml, scraper, and record cases for the behavior it does not cover

**D50** (dependency pil): pil maps to image only in part (used by 3 units). Use it?

> Use image, and record cases for the behavior it does not cover

**D51** (dependency numpy): numpy maps to ndarray only in part (used by 2 units; Broadcasting and dtype rules differ; check numerics). Use it?

> Use ndarray, and record cases for the behavior it does not cover

**D52** (dependency yaml): yaml maps to serde_yaml_ng, saphyr only in part (used by 2 units; Round-tripping comments is not covered). Use it?

> Use serde_yaml_ng, saphyr, and record cases for the behavior it does not cover

**D53** (dependency psycopg2): psycopg2 maps to sqlx only in part (used by 1 unit; ORM layers port by hand). Use it?

> Use sqlx, and record cases for the behavior it does not cover

**D54** (tangled units): pyUltroid/, pyUltroid/_misc/, pyUltroid/dB/, pyUltroid/fns/, pyUltroid/startup/, strings/ import each other (6171 lines). Port them as one piece?

> Yes: one piece in wave 0, no glue between its parts

