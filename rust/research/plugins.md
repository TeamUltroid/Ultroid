# Plugins in a Rust Ultroid: evidence for ADR-006

Research only: trade-offs, no recommendation. Written 2026-11-20 from this checkout and from primary sources (`cargo info`, docs.rs, crates.io, each project's own documentation and repository). Nothing was run against Telegram; statements about Ultroid come from reading the code and from the commands shown. Quoted fragments are short; the URL next to each has the full text. "Inference" marks reasoning from cited facts that no source states.

## Summary

- A plugin today is a Python file that is imported (official) or executed with an injected namespace (addon). 84 files in `plugins/` and 16 in `assistant/` carry 448 handler decorators for two Telethon clients. Addons arrive from a git repository, a chat message, a URL or a Telegram channel.
- Plugins are written against Telethon and the `plugins` namespace, not against a narrow plugin API: 49 of 83 import `telethon` directly, and together they call 36 client methods and build 30 raw request types.
- The one check on loaded code, a scan with 11 regular expressions, runs only for the `.install` command and is skipped by `install f`. `.getaddons`, `.load`, plugin channels and the addons repository load code without it. A loaded plugin is arbitrary code in the process that holds the session.
- Embedding CPython with PyO3 is the only option for which the sources support running today's plugin files unchanged, and only while Telethon keeps running inside the interpreter; otherwise a Telethon-compatible layer has to be written. PyO3 documents no sandbox and does not support sub-interpreters.
- A compiled-in registry and dynamic libraries both mean rewriting every plugin in Rust. The registry ends installation from chat; dynamic libraries keep it only as native code, and the Rust ABI has no stability guarantee.
- WebAssembly (wasmtime, Extism), Rhai and mlua document ways to confine plugin code. In each the host must define and implement every capability a plugin may use, and no existing plugin runs unchanged.
- RustPython keeps Python syntax, but the project calls itself not production-ready and says its build supports about half of the standard library. Whether Telethon or the C-extension packages used by plugins run on it was not verified.

## 1. How plugins work today

Paths are relative to the repository root.

### 1.1 Counts, with the commands that produce them

```sh
ls plugins/*.py | wc -l                  # 84 = 83 plugins + __init__.py (6 plugins are named _*.py)
cat plugins/*.py | wc -l                 # 16061 lines; 14393 non-blank (rust/PLAN.md counts 14394)
find assistant -name '*.py' | wc -l      # 16 = 9 in assistant/ + 7 in assistant/manager/
for d in '@ultroid_cmd' '@callback' '@in_pattern' '@asst_cmd' '@ultroid_bot\.on' '@asst\.on'; do
  echo "$d $(grep -rhE "^\s*$d\b" plugins assistant --include='*.py' | wc -l)"; done
# @ultroid_cmd 293, @callback 100, @in_pattern 24, @asst_cmd 17, @ultroid_bot.on 11, @asst.on 3
# total 448 decorators: 341 in plugins/ (291, 27, 11, 1, 11, 0), 107 in assistant/ (2, 73, 13, 16, 0, 3)
grep -rhE '\.add_(event_)?handler\(' plugins assistant --include='*.py' | wc -l   # 26 direct registrations
g() { grep -rlE "$1" --include='*.py' --exclude-dir=rust --exclude-dir=.git .; }
g '(^|[^A-Za-z0-9_.])eval\s*\('   # 3 files: pyUltroid/fns/tools.py plugins/nightmode.py plugins/calculator.py
g '(^|[^A-Za-z0-9_.])exec\s*\('   # 1 file:  plugins/devtools.py
g 'importlib'                     # 2 files: pyUltroid/loader.py pyUltroid/startup/utils.py
g '__import__'                    # 1 file:  pyUltroid/fns/helper.py (text of a scan pattern, not a call)
g 'subprocess\.|os\.system|create_subprocess_(shell|exec)'   # 10 files, 2 of them in plugins/
grep -rlE '\bbash\(' plugins --include='*.py' | wc -l        # 15 plugin files run shell commands via bash()
```

### 1.2 Discovery and import

- `Loader.load` (`pyUltroid/loader.py:24-77`) globs `<path>/*.py` (`:48`) and drops the names in an exclude list unless they start with `_` (`:49-53`); with an include list it takes every `_*.py` plus the listed names (`:34-41`). It sorts the paths and calls `importlib.import_module` on each (`:58-62`). A failing import is logged and skipped (`:63-71`).
- Start-up order is `load_other_plugins` (`pyUltroid/startup/loader.py:48-144`): `plugins/` filtered by `EXCLUDE_OFFICIAL` / `INCLUDE_ONLY` (`:51-57`), then, each behind its own setting, `assistant/` (`:60-66`), addons (`:69-112`), `assistant/manager` (`:117`), `assistant/pmbot.py` (`:121`) and the VcBot repository, cloned and imported (`:124-144`).
- Addons: `git clone` of `ADDONS_URL`, or of `TeamUltroid/UltroidAddons` on the branch named like the current one, else `git pull` (`pyUltroid/startup/loader.py:70-90`); `pip install -r addons/addons.txt` (`:91-99`); every `.py` under `addons/` goes to `load_addons` (`:106-112`).
- Plugin channels: every `.py` document in each chat of `PLUGIN_CHANNEL` is downloaded into `addons/` and passed to `load_addons` (`pyUltroid/startup/funcs.py:432-466`, called from `pyUltroid/__main__.py:77-84`).
- Help text is the module docstring or a language string, collected after import into the `HELP` registry (`pyUltroid/startup/loader.py:23-45`; registries in `pyUltroid/dB/_core.py:8-13`).

### 1.3 The namespace a plugin gets

- An official plugin takes its names from `plugins/__init__.py`: star-imports of `pyUltroid`, `pyUltroid.fns.helper`, `.misc` and `.tools` (`:17`, `:22-24`), the decorators and `eor`/`eod` (`:18-20`), Telethon's `Button`, `events`, `functions`, `types` (`:14-15`), and shared mutable state `List`, `Dict`, `InlinePlugin`, `STUFF` (`:58-63`). All 83 plugins import from it (`grep -lE '^\s*from \. import' plugins/*.py | wc -l`), 74 distinct names in total (counted with Python's `ast` module over the `from . import` statements); `plugins/devtools.py:23` and `plugins/pmpermit.py:66` use `from . import *`.
- An addon is not imported. `load_addons` (`pyUltroid/startup/utils.py:31-99`) creates a module named `addons.<file>` (`:46-48`), sets 33 attributes on it before running it (both clients, `udB`, the decorators, `eor`, `HNDLR`, ...; `:52-84`) and executes it (`:86`).
- The addons repository's `__init__.py` is `from plugins import *` followed by `bot = ultroid_bot` (https://raw.githubusercontent.com/TeamUltroid/UltroidAddons/main/__init__.py); `pyUltroid/startup/funcs.py:443-445` writes the same text. Two sampled addons, `figlet.py` and `hack.py`, import with `from . import ...` and register with `@ultroid_cmd` (https://raw.githubusercontent.com/TeamUltroid/UltroidAddons/main/figlet.py).
- `eor` and `try_delete` are patched onto Telethon's `Message` class (`pyUltroid/_misc/_wrappers.py:64-65`). The client class extends one from the `telethonpatch` package (`pyUltroid/startup/BaseClient.py:14`, `:28`; `requirements.txt:5`).

### 1.4 Handler registration

- `ultroid_cmd` (`pyUltroid/_misc/_decorators.py:69-346`) wraps the function with permission checks (`:96-125`: owner, sudo, full sudo, `#noub` chats, groups or admins only, `only_devs`) and error reporting to the log channel (`:126-230`). It registers the wrapper with `add_event_handler` up to five times: sudo prefix (`:242`), own prefix (`:255`), edited messages (`:271`), the assistant as group manager (`:308`), dual mode (`:322`). `compile_pattern` builds the regex from prefix and pattern (`:58-66`).
- It identifies the calling plugin with `inspect.stack()[1].filename` (`:333`), records the wrapper in `LOADED` only when that path contains `addons/` (`:334-338`), and records the pattern in `LIST` (`:339-343`).
- `asst_cmd`, `callback` and `in_pattern` register on the bot client (`pyUltroid/_misc/_assistant.py:45-66`, `:69-92`, `:95-152`).
- Plugins also register by hand (the 26 calls in 1.1), and two start scheduler jobs at import when their database keys are set (`plugins/nightmode.py:147-155`, `plugins/autopic.py:131-154`).
- `TAKE_EDITS`, `MANAGER`, the chat blacklist and the sudo switch are read once, when the decorator module is imported (`pyUltroid/_misc/_decorators.py:52-55`).

### 1.5 Installing, loading and unloading at runtime

- `.install` (`plugins/core.py:21-23`, `safeinstall` in `pyUltroid/fns/helper.py:151-204`): reply to a `.py` document. The file is downloaded to `addons/` (`:172`), scanned (1.6) unless the command is `install f` (`:173`), then run by `load_addons` (`:182`).
- `.getaddons <raw link>` (`plugins/core.py:97-124`) downloads a URL into `addons/` and runs it. `.load <name>` (`plugins/core.py:72-94`) calls `un_plug`, then runs `addons/<name>.py` again. Neither is scanned.
- These three need `fullsudo=True`: an incoming command is refused unless the sender is the owner or in `FULLSUDO` (`pyUltroid/_misc/_decorators.py:96-107`, `pyUltroid/_misc/__init__.py:45-54`).
- `.unload` and `.uninstall` (`plugins/core.py:26-69`) work on addons only and refuse official plugins (`:43`, `:66`). Any sudo user may run them.
- `un_plug` (`pyUltroid/fns/helper.py:122-146`) removes the handlers recorded in `LOADED[name]` from both clients (`:126-130`). Its fallback deletes entries of Telethon's private `client._event_builders` whose callback module is `addons.<name>` (`:135-140`). It does not touch `sys.modules`, scheduled jobs or patched classes.
- Reading of the code: handlers an addon registers through `asst_cmd`, `callback` or `in_pattern` are covered by neither path, because their wrappers are defined in `pyUltroid/_misc/_assistant.py` and are not put in `LOADED`.
- `addons/` is ignored by git (`.gitignore:23`). At start an `addons/` directory without `.git` is deleted when addons or plugin channels are enabled (`pyUltroid/startup/loader.py:72-73`, `pyUltroid/startup/funcs.py:439-440`).

### 1.6 The safety scan

- `KEEP_SAFE.All` is 11 regular expressions (`pyUltroid/fns/helper.py:82-97`): `os.system`, `subprocess.(run|call|Popen|check_output)`, `exec(`, `eval(`, `__import__(`, `open(` with `"w"`, `shutil.(rmtree|move|copy)`, `session.string`, `get_me()`, `api_id`, `api_hash`.
- It is used in two places: `safeinstall`, with `re.search` over the file text (`pyUltroid/fns/helper.py:174-180`), and `.eval` for senders other than the owner (`plugins/devtools.py:241-251`).
- `.eval` tests the patterns with `in` (substring), not `re.search`. Run outside the bot, only `api_id` and `api_hash`, the two patterns without regex syntax, matched their own target text that way.
- It is a text match. `import os as o; o.system(...)`, `from os import system` and `importlib.import_module("os")` matched none of the 11 patterns in the same check.
- It does not run for `install f`, `.getaddons`, `.load`, plugin channels, the addons repository or official plugins.

### 1.7 Where code is evaluated or a shell is run

- `.eval` calls `aexec`, which runs `exec(wrapped_code, exec_globals)` with the module globals, the event and the client in scope (`plugins/devtools.py:200`, `:326-356`). `.bash` runs `asyncio.create_subprocess_shell` (`plugins/devtools.py:65-80`, `pyUltroid/fns/helper.py:273-287`). `.cpp` writes a file, runs `g++` and then the binary (`plugins/devtools.py:368-404`).
- `.eval` and `.bash` need full sudo and the database key `I_DEV`; `.cpp` needs only `I_DEV` (`plugins/devtools.py:65`, `:200`, `:368`; `pyUltroid/_misc/_decorators.py:120`).
- Other `eval` calls: on a database value (`plugins/nightmode.py:128`, `:151`), on text built from inline button presses (`plugins/calculator.py:108`), and in the fallback YAML reader (`pyUltroid/fns/tools.py:1054`).
- `sys.executable` appears 20 times in 7 files (`grep -rhoE 'sys\.executable'` with the options of `g` in 1.1), to restart the process and to run `pip` (for example `pyUltroid/fns/helper.py:612`, `pyUltroid/startup/loader.py:97`, `plugins/bot.py:227`).

### 1.8 Shims for plugins written for other userbots

- `load_addons` points 14 foreign module paths (`userbot`, `userbot.utils`, `telebot`, `fridaybot`, `uniborg.util`, ...; `pyUltroid/startup/utils.py:13-28`) and `pyUltroid.functions` at Ultroid modules in `sys.modules` (`:49-51`), and injects other bots' names for the client and helpers (`borg`, `telebot`, `jarvis`, `friday`, `tgbot`, `on_cmd`, `edit_or_reply`, `CMD_HELP`, ...; `:52-84`).
- `pyUltroid/_misc/_supporter.py` ("To Install Other USERBOTs plugin Support", `:8`) supplies `admin_cmd`, `sudo_cmd`, `register`, `command`, `friday_on_cmd`, `catub.cat_cmd` and a `Config` class (`:30-31`, `:36-67`, `:77-123`).
- Both rely on replacing entries in `sys.modules` and on setting attributes on a module object before it runs.

### 1.9 What the 83 in-repo plugins take from the host

```sh
grep -lE '^\s*(from|import) telethon' plugins/*.py | wc -l                          # 50 = 49 plugins + __init__.py
grep -rhoE '(\.client|\bultroid_bot|\basst)\.[a-z_]+\(' plugins --include='*.py' \
  | sed -E 's/.*\.([a-z_]+)\($/\1/' | sort -u | wc -l                               # 36 client methods, 424 calls
grep -rhoE '\b[A-Z][A-Za-z]+Request\(' plugins --include='*.py' | sort -u | wc -l   # 30 raw request types
grep -lE '^\s*(from|import) (PIL|cv2|numpy|skimage)(\.|\s|$)' plugins/*.py | wc -l  # 13 files, C-extension packages
```

- Event objects: `.eor(` 662 call sites in 79 files, `.pattern_match` 189 in 68, `get_reply_message(` 131 in 52, `isinstance(` 68 in 24, most of the last against Telethon types such as `User`, `Channel`, `Chat` and `UserStatus*`. Command: `grep -rhoE 'P' plugins --include='*.py' | wc -l` (and `-rlE` for files) with `P` = `\.eor\(`, `\.pattern_match`, `get_reply_message\(`, `isinstance\(`.
- Also used: the key-value database `udB` (36 plugins, pattern `\budB\.`), HTTP through `aiohttp` and `requests`, the file system, subprocesses (15 files) and the `apscheduler` scheduler (2 files). Figures for the whole app, not only `plugins/`, are in `research/telethon.md`.

## 2. Options if the core were Rust

Crate versions and licences are from `cargo info <crate>` on 2026-11-20. None of these crates provides the Telegram side; that is ADR-005 (`research/telethon.md`) and still open.

### 2a. Embed CPython with PyO3 and keep the Python plugins

Crates: `pyo3` 0.30.1 (MIT OR Apache-2.0, rust-version 1.85); `pyo3-async-runtimes` 0.30.0 (Apache-2.0, rust-version 1.85).

- Embedding is a supported use: "You can use PyO3 to write a native Python module in Rust, or to embed Python in a Rust binary." Supported: "CPython 3.9 or greater". (https://pyo3.rs/v0.30.1/) The crates on this branch are bridged to CPython in the first form (ADR-010).
- Python stays a runtime dependency: "To embed Python into a Rust binary, you need to ensure that your Python installation contains a shared library." (https://pyo3.rs/v0.30.1/) With dynamic embedding "when the OS runs your Rust program it also needs to be able to find the Python shared library"; for static embedding "PyO3 does not yet have first-class support for this embedding mode"; "PyPy cannot be embedded in Rust (or any other software)". (https://pyo3.rs/v0.30.1/building-and-distribution.html)
- The `auto-initialize` feature makes PyO3 "start a Python interpreter on first call to `Python::attach`" (https://pyo3.rs/v0.30.1/); without it "you should call `Python::initialize()` before attempting to call any other Python APIs" (https://pyo3.rs/v0.30.1/features.html). It is "deliberately disabled when embedding the interpreter statically" (https://pyo3.rs/v0.30.1/building-and-distribution.html). `initialize` starts Python "with signal handling disabled" (https://docs.rs/pyo3/0.30.1/pyo3/marker/struct.Python.html).
- Loading code: `PyModule::import` can "import and use any Python module available in your environment". `PyModule::from_code` makes a module from source text, which the guide reads at run time with `std::fs::read_to_string`, and warns "Never pass untrusted code to this function!". Rust-implemented modules are added with `append_to_inittab`, which "must be invoked before initializing Python". (https://pyo3.rs/v0.30.1/python-from-rust/calling-existing-code.html) Rust calls into Python with `call` ("call any callable Python object") and `call_method` (https://pyo3.rs/v0.30.1/python-from-rust/function-calls.html).
- Threads: "Calling into the CPython C API is only legal when an OS thread is explicitly attached to the interpreter runtime." "Since version 0.23, PyO3 supports building Rust extension modules for the free-threaded Python build"; the page does not discuss embedding a free-threaded interpreter. (https://pyo3.rs/v0.30.1/free-threading.html) With the GIL, "only one thread executes Python bytecode at a time" (https://docs.python.org/3/glossary.html).
- Isolation: sub-interpreters are not supported. The issue has been open since 2019-08-14; a maintainer wrote "PyO3 is some way off supporting sub-interpreters." (https://github.com/PyO3/pyo3/issues/576)
- Async: PyO3's own `async fn` support is the `experimental-async` feature, "still in active development" (https://pyo3.rs/v0.30.1/async-await.html). `pyo3-async-runtimes` converts in both directions (`into_future`, `future_into_py`) between "separate Python and Rust event loops", because "we don't have a way to run Rust futures directly on Python's event loop"; "only the Async-Std and Tokio runtimes are supported" (https://docs.rs/pyo3-async-runtimes/0.30.0/pyo3_async_runtimes/). Its README describes the design as to "surrender the main thread to Python" and "run Rust's event loops in the background" (https://github.com/PyO3/pyo3-async-runtimes).
- A Rust type exposed with `#[pyclass]` can inherit only from "classes defined in Rust and builtins provided by PyO3"; "inheriting from other classes defined in Python is not yet supported" (https://pyo3.rs/v0.30.1/class.html).

What the plugins would still need from the host. PyO3 supplies an interpreter, not Telegram. The plugins call Telethon client methods and receive Telethon event objects (1.9), so one of two things has to hold:

1. Telethon keeps running inside the embedded interpreter and owns the session. Then the client, event dispatch, decorators and loaders stay Python and the Rust program is a host around them. Rust cannot be assumed able to use the same session on a second connection: Telegram documents `AUTH_KEY_DUPLICATED` for "an authorized session ... sending requests in parallel" from "two separate TCP connections", after which "the session was already invalidated by the server" (https://core.telegram.org/api/errors; the page also describes server-granted parallel sessions).
2. A Rust client owns the session (library undecided, ADR-005) and Python sees a layer with Telethon's names and behaviour: importable `telethon.*` modules, the 36 client methods, the event methods, the 30 request types, the error classes, and objects that satisfy the plugins' `isinstance` checks. By the `#[pyclass]` rule a Rust class cannot inherit from Telethon's classes, so (inference) those objects must come from classes the layer defines itself or be built in Python from real Telethon classes. How much of Telethon the addons need is unknown (section 3).

In both cases every handler is an `async def` that needs an asyncio loop, plus the namespace of 1.3. Consequences:

- In-repo plugins: keep as is (case 1) or keep with a compatibility layer (case 2). Addons repository: the same; the shims of 1.8 keep working because the interpreter is still CPython.
- Install from chat: survives, since source text is loaded at run time. `.eval` survives.
- Deployment (inference from the quotes above and `requirements.txt`): the Rust binary needs the Python shared library and the installed packages at run time. Code that relies on `sys.executable` (1.7) must be checked: Python documents it as the interpreter's own binary, or "an empty string or `None`" when that is unknown (https://docs.python.org/3/library/sys.html). Its value under PyO3 embedding was not verified.
- Security: the same as today. Plugin code runs in the host process with everything the interpreter can do, and the sources describe no sandbox and no per-plugin isolation. The scan of 1.6 can be kept with the same limits.

### 2b. Plugins compiled into the binary behind a registry

Crates: `inventory` 0.3.25 (MIT OR Apache-2.0, rust-version 1.68); `linkme` 0.3.38 (MIT OR Apache-2.0, rust-version 1.71).

- `inventory`: "Typed distributed plugin registration."; "all `submit!` invocations across all source files linked into your application all take effect simultaneously" (https://docs.rs/inventory/0.3.25/inventory/). Registration happens "as part of life-before-main for statically linked elements"; platforms are "Linux, macOS, iOS, FreeBSD, Android, Windows, WebAssembly, and a few others", and elsewhere "no plugins have been registered"; "There is no guarantee about the order" of iteration (https://github.com/dtolnay/inventory).
- `linkme`: a distributed slice whose elements "may be defined individually from anywhere in the dependency graph of the final binary"; it "does not involve life-before-main or any other runtime initialization on any platform". Its platform table lists Linux, macOS, Windows, FreeBSD, OpenBSD and illumos. (https://github.com/dtolnay/linkme)
- Inference: both collect items that are linked into the binary, so a new plugin means a new build. Neither loads code at run time. Today's load order is sorted by path (`pyUltroid/loader.py:58`); with `inventory` the host would have to sort.

Consequences:

- In-repo plugins: rewrite all 83 in Rust; each Python package they use needs a Rust counterpart (ADR-009, `research/dependencies-plugins.md`). Addons repository: rewrite as Rust code that is compiled in, or drop. The shims of 1.8 have no equivalent.
- Install from chat: does not survive. Switching compiled-in plugins on and off at run time remains possible (inference: the host chooses which registry entries to register). `.eval` of Python does not survive without an interpreter.
- Security: no code enters at run time, so what runs is what was compiled. A compiled plugin still has the whole account.

### 2c. Plugins as dynamic libraries

Crates: `libloading` 0.9.1 (ISC, rust-version 1.88); `abi_stable` 0.11.3 (MIT/Apache-2.0, rust-version 1.61; 0.11.3 was published 2023-10-12, https://crates.io/api/v1/crates/abi_stable).

- Rust: "The Rust ABI offers no stability guarantees."; the C ABI "matches the default ABI chosen by the dominant C compiler for the target" (https://doc.rust-lang.org/reference/items/external-blocks.html). "Type layout can be changed with each compilation." (https://doc.rust-lang.org/reference/type-layout.html)
- `libloading`: "Bindings around the platform's dynamic library loading primitives with greatly improved memory safety." (https://docs.rs/libloading/0.9.1/libloading/) Loading is `unsafe`: "When a library is loaded, initialisation routines contained within it are executed."; callers "must specify the correct type of the function or variable loaded"; closing "might be a no-op". (https://docs.rs/libloading/0.9.1/libloading/struct.Library.html)
- `abi_stable`: "For Rust-to-Rust ffi, with a focus on creating libraries loaded at program startup, and with load-time type-checking."; libraries may be "built with a different Rust version than the crate that depends on it"; a listed use is "Creating a plugin system (without support for unloading)." (https://docs.rs/abi_stable/0.11.3/abi_stable/) Its README says it "assumes that dynamic libraries come from a benign source", that "these checks are done purely to detect programming errors", and lists library unloading under "Non-features (extremely unlikely to be added)" (https://github.com/rodrimati1992/abi_stable_crates).
- `inventory` adds that elements in a dynamically loaded library "are registered at the time that dlopen occurs" (https://github.com/dtolnay/inventory).

Consequences:

- In-repo plugins: rewrite all in Rust, or in another language that can produce a C-ABI library. Addons repository: rewrite; inference: it would ship one binary per operating system and CPU, or source that each host compiles.
- Install from chat: a library file can be loaded at run time, but it is machine code for one platform and the text scan of 1.6 has nothing to read. Unloading: not with `abi_stable`; platform dependent with `libloading`.
- Security: not better than today and harder to inspect. The library is native code in the host process and its initialisers run at load.

### 2d. WebAssembly plugins

Crates: `wasmtime` 51.0.0 and `wasmtime-wasi` 51.0.0 (Apache-2.0 WITH LLVM-exception, rust-version 1.97.0); `extism` 1.41.0 (BSD-3-Clause, depends on `wasmtime` 49); `extism-pdk` 1.4.1 (BSD-3-Clause).

- Sandbox: "WebAssembly is inherently sandboxed by design (must import all functionality, etc)."; "the only thing a WebAssembly instance can do is what is available through interfaces it has been explicitly linked with"; "all accesses within linear memory are checked to ensure they stay in bounds" (https://docs.wasmtime.dev/security.html).
- A default WASI context has "no preopens" and "no env vars", and "TCP/UDP are allowed but all addresses are denied by default." (https://docs.rs/wasmtime-wasi/51.0.0/wasmtime_wasi/struct.WasiCtxBuilder.html)
- Runaway code: fuel is "completely deterministic" but has more overhead; epochs have "relatively low overhead" and are not deterministic (https://docs.wasmtime.dev/examples-interrupting-wasm.html). `ResourceLimiter` is "Used by hosts to limit resource consumption of instances." (https://docs.rs/wasmtime/51.0.0/wasmtime/)
- Component model: the API is written in WIT, which "defines only contracts between components" (https://component-model.bytecodealliance.org/design/wit.html). A component "interacts with a runtime or other components only by calling its imports and having its exports called" (https://component-model.bytecodealliance.org/design/why-component-model.html). `bindgen!` "generates traits for embedders to implement" (https://docs.rs/wasmtime/51.0.0/wasmtime/component/index.html).
- Async and languages: async host functions are supported, and "Wasmtime supports executing WebAssembly guests through Rust-level `async` functions." (https://docs.rs/wasmtime/51.0.0/wasmtime/) Guest languages documented: C/C++, C#, Dart, Go, JavaScript, Python, Rust, MoonBit; "the level of support varies across languages" (https://component-model.bytecodealliance.org/language-support.html).
- Loading at run time: `Component::new` takes bytes, "the binary or text format of a WebAssembly component" (https://docs.rs/wasmtime/51.0.0/wasmtime/component/struct.Component.html).
- Targets: x86_64 Linux is Tier 1, aarch64 Linux Tier 2, aarch64 and x86_64 Android Tier 3; the component model is Tier 1 (https://docs.wasmtime.dev/stability-tiers.html).
- Extism is "a lightweight framework for building with WebAssembly (Wasm)" with "runtime limiters & timers" and "host-controlled HTTP without WASI"; it lists plug-in kits for Rust, JS, Python, Go, Haskell, AssemblyScript, .NET, C, C++ and Zig (https://github.com/extism/extism).
- Extism controls. Manifest fields: `allowed_hosts` ("if this is empty then no hosts may be accessed"), `allowed_paths`, `timeout_ms` (https://docs.rs/extism-manifest/latest/extism_manifest/struct.Manifest.html, showing 1.41.0). `with_wasi` "Enables WASI if the argument is set to `true`" and `with_fuel_limit` "Limits fuel consumed during each plugin call." (https://docs.rs/extism/1.41.0/extism/struct.PluginBuilder.html) Host functions "make it possible for a plug-in to invoke host application code" (https://extism.org/docs/concepts/host-functions).
- Python inside WebAssembly exists with limits. Extism's Python PDK "only works with pure Python dependencies", "packages that require native shared libraries aren't supported", and "`wasi` must be provided for all Python plug-ins" (https://github.com/extism/python-pdk). `componentize-py` "can only import dependencies during build time" (https://github.com/bytecodealliance/componentize-py).

What the host must expose (inference from 1.9 and from the rule that a guest has only its imports): every Telegram operation plugins use (send, edit, delete, download, upload, entity lookup, admin actions, inline queries, conversations, raw requests), event delivery with pattern matching, the database, HTTP, files, time and scheduling, and for 15 plugin files a way to run programs such as `ffmpeg`. Each import granted is an opening of exactly that size: an import that sends any raw request hands a plugin the whole account. Consequences:

- In-repo plugins: rewrite all against the new API, in any language with a guest toolchain. Keeping Python source would need Python-in-WebAssembly plus a Telethon-like shim, under the limits above (13 plugin files import C-extension packages); feasibility not verified. Addons repository: rewrite; the shims of 1.8 go.
- Install from chat: survives as a compiled `.wasm` file, not as `.py` source.
- Security: differs from today. By the statements above a plugin can do only what its imports allow, with bounded CPU and memory if the host sets limits; the session stays in the host unless an import exposes it.

### 2e. An embedded scripting language

Crates: `mlua` 0.12.2 (MIT, rust-version 1.88); `rhai` 1.27.0 (MIT OR Apache-2.0, rust-version 1.66.0); `rustpython` 0.6.0 and `rustpython-vm` 0.6.0 (MIT, rust-version 1.95.0; 0.6.0 is dated 2026-10-02, https://docs.rs/crate/rustpython/0.6.0).

- `mlua` "supports Lua 5.5, 5.4, 5.3, 5.2, 5.1 (including LuaJIT) and Luau" and "supports async/await for all Lua versions including Luau"; the `vendored` feature builds the Lua C sources during compilation. On safety it says it "does not provide absolute safety even without using `unsafe`" and "contains a huge amount of unsafe code". (https://github.com/mlua-rs/mlua)
- `mlua` API: `Lua::new` "loads the safe subset of the standard libraries" and "will not allow to load unsafe standard libraries or C modules"; `Lua::load` takes "Lua source code"; `create_async_function` "Wraps a Rust async function or closure"; there is `set_memory_limit`; `sandbox` needs Luau. (https://docs.rs/mlua/0.12.2/mlua/struct.Lua.html)
- `rhai`: "Rhai is sand-boxed so a script can never read from outside its own environment." (https://rhai.rs/book/safety/sandbox.html) "Protected against malicious attacks – such as stack-overflow, over-sized data, and runaway scripts etc." (https://rhai.rs/book/about/features.html) "No classes", "No first-class functions", "No JIT" (https://rhai.rs/book/about/non-design.html).
- `rhai` API: `Engine::eval` will "Evaluate a string as a script", `register_fn` will "Register a custom function with the Engine", and `set_max_operations` caps the operations a script may run (https://docs.rs/rhai/1.27.0/rhai/struct.Engine.html). "Async and scripting don't mix well": the documented pattern runs the engine on its own thread, which "blocks on the function call, waiting for a reply message on the reply channel" (https://rhai.rs/book/patterns/blocking.html).
- `rustpython`, in the project's words: "not totally production-ready" (https://github.com/RustPython/RustPython); "should not be used in production or a fault intolerant setting" and "Our current build supports only about half of the Python standard library." (https://rustpython.github.io/)
- RustPython's "What's left" page lists 6 public modules (`cProfile`, `curses`, `profiling`, `readline`, `xxlimited_35`, `xxlimited_3_13`) and 15 private ones as missing, and notes that "not every module here is critical or feasible" (https://rustpython.github.io/pages/whats-left, as fetched 2026-11-20). That list and "about half" both come from the project's site; this file does not reconcile them. Target version: the README on `main` says "CPython >= 3.15.0" (https://raw.githubusercontent.com/RustPython/RustPython/main/README.md), the 0.6.0 crate README "CPython >= 3.14.0" (https://docs.rs/crate/rustpython/0.6.0), the website "CPython >= 3.11.0" (https://rustpython.github.io/).
- CPython extension modules on RustPython: `rustpython-capi` 0.6.0 is described as "Minimal CPython C-API compatibility exports for RustPython" (`cargo info rustpython-capi`); its tracking issue reports "Total missing: 220" Stable ABI functions, last updated 2026-10-30 (https://github.com/RustPython/RustPython/issues/8156).

Consequences:

- Lua or Rhai. In-repo plugins and addons: rewrite all in the new language, against a host API as wide as in 2d (inference: a script reaches only what the host registers). Install from chat: survives, a script is text. `.eval` would evaluate that language, not Python. Security: differs from today if the registered API is narrow and the unsafe libraries stay unloaded; the script runs in the host process, so it rests on the interpreter (see mlua's own caveat).
- RustPython. It would keep Python source without CPython. Plugins would still need Telethon or a shim as in 2a, their third-party packages, and C extensions for 13 files. Whether Telethon 1.44 runs on RustPython 0.6.0 is not verified. Install from chat would survive (inference: source text is loaded at run time, as in 2a). Security: not verified; the pages read describe no sandbox.

### 2.6 Comparison

| Option | 83 in-repo plugins | Addons repository | Install from chat | Security compared with today | Host has to provide |
| --- | --- | --- | --- | --- | --- |
| 2a, Telethon stays in the interpreter | keep as is | keep as is | yes, `.py` | same | CPython and packages at run time; Telegram path stays Python |
| 2a, Rust owns the session | keep with a compatibility layer | same layer; coverage unknown | yes, `.py` | same | Telethon-compatible Python API on a Rust client; two event loops |
| 2b `inventory` / `linkme` | rewrite all in Rust | rewrite or drop | no | no code enters at run time; a plugin still has the whole account | plugin trait and registry |
| 2c `libloading` / `abi_stable` | rewrite all in Rust | rewrite; binaries per platform | only as a native library | same access; native and unscannable | C-ABI or `abi_stable` interface |
| 2d `wasmtime` / `extism` | rewrite all | rewrite | yes, `.wasm` | limited to granted imports | the whole plugin API as imports; limits |
| 2e `mlua` / `rhai` | rewrite all | rewrite | yes, script text | limited to registered functions, in-process | the whole plugin API as registered functions |
| 2e `rustpython` | keep only if Telethon or a shim runs there: not verified | same: not verified | yes, `.py` | not verified | as 2a, plus whatever stdlib and C extensions are missing |

The cells condense 2a to 2e, including the inferences marked there.

## 3. What is still unknown

Decisions that belong to the maintainers:

1. Whether code from third parties must keep loading at run time at all: the addons repository, `.install`, `.getaddons`, plugin channels, the shims for other userbots. 2b says no; the others keep it in some form.
2. Whether a plugin having the whole account stays acceptable. Only 2d and Lua/Rhai in 2e change that, and only as far as the host API is kept narrow.
3. ADR-005, the Telegram library. It decides whether "Telethon stays" is the only way to keep plugins unchanged, and what API 2b to 2e can offer.
4. What happens to `.eval`, `.bash` and `.cpp`. Python `.eval` exists only where a Python interpreter exists.
5. Target platforms (ADR-010, Termux). Each option adds a runtime or build requirement: a Python shared library (2a), the Lua C library, vendored or otherwise (2e), wasmtime's Tier 3 Android targets (2d).

Things to measure:

1. The API surface used by addons. UltroidAddons is not in this checkout (`addons/` is absent and git-ignored); its `main` branch shows at least 95 `.py` files (see "Not verified"). How many addons still use the shims of 1.8.
2. For 2a with a Rust client: how much Telethon behaviour the layer must reproduce for the 448 decorators. 1.9 is the starting list for in-repo plugins only.
3. Cost per event of crossing Rust to Python or host to guest, plus memory and start-up time of each runtime. No source read here gives numbers for this workload.
4. Whether Telethon with `telethonpatch` runs correctly in an interpreter embedded by PyO3 under the loop arrangement `pyo3-async-runtimes` describes, what the `sys.executable` restart and `pip` calls do there, and whether the deployment image (`Dockerfile:6`, started by `startup:19`) ships a Python shared library.
5. Whether RustPython 0.6.0 runs Telethon and the plugins' packages; whether Python-in-WebAssembly runs plugin-sized asyncio code.
6. How a rewrite would be proven. ADR-001 needs recorded behaviour, there is no account to record plugins against, and `rust/PLAN.md` counts 0 test files. 2b, 2c, 2d and Lua/Rhai are rewrites of the 14,393 non-blank plugin lines.
7. Which unload behaviour is required. Today's is partial (1.5).

Not researched: plugins in a separate process that talks to a Rust core; other engines such as `wasmer`, `wasmi`, `stabby` or JavaScript runtimes.

## Not verified

- The number of files in UltroidAddons. Tried: the GitHub API tree listing (HTTP 403) and the HTML listing of `main` (https://github.com/TeamUltroid/UltroidAddons/tree/main, cut at 100 entries, 95 of them `.py`, last one `videotools.py`). The repository was not cloned. The listing includes names that also exist in `plugins/`, such as `afk.py`; that overlap was not examined.
- Which Telethon APIs, Python packages and shims the addons use. Only `__init__.py`, `figlet.py` and `hack.py` were read.
- Everything in section 1 that describes run-time behaviour was read from the code, not observed in a running bot (no Telegram account here, ADR-001). The scan results in 1.6 come from running the 11 patterns in a scratch interpreter.
- Whether Telethon runs on RustPython. Tried: the README, the website, the "What's left" page and a search of the repository, which showed pull requests syncing `asyncio` with CPython 3.15 but no statement of support. The regression-test results page was too large to fetch. Nothing was installed or run.
- Whether RustPython can load Pillow, NumPy or OpenCV through `rustpython-capi`. The docs.rs page has no prose; the tracking issue lists missing functions only.
- Whether RustPython offers any sandboxing, and what its `host_env` feature controls. No statement found on the pages read.
- `componentize-py`: support for native extensions, `asyncio`, sockets and the bundled CPython version. Its README states only the build-time import limit.
- Extism: whether a plug-in call can be awaited or runs concurrently, and whether the Python PDK supports `asyncio`. The pages read do not say.
- Rhai: a statement that the engine has no async API. The book page has only the warning quoted in 2e and the thread-and-channel pattern.
- `wasmtime-wasi`: the default of `allow_tcp` / `allow_udp`. Two fetches of the same page gave wording that conflicts with the `WasiCtxBuilder::new` defaults quoted in 2d; only the latter is relied on.
- `linkme` on Android/Termux. Its table does not list Android and does not say it is unsupported.
- PyO3 embedding on Termux. The guide mentions Android only in the cross-compilation notes.
- Embedding a free-threaded CPython with PyO3, and whether Telethon and the plugins' packages support that build. The free-threading page covers extension modules only.
- The value of `sys.executable` in an interpreter embedded with PyO3.
- That PyO3 offers no sandbox. This is an absence: the pages cited in 2a and a search of pyo3.rs for "sandbox" turned up none.
- Performance of any option, and licence compatibility of these crates with Ultroid's AGPL licence. Neither was assessed.
