# Ultroid — Core Refactor & Modernization

Date: 2026-01-28
Branch: `refactor/core-modernization`
Target: Python **3.10+** (preserves `telethonpatch` — the project's vendored
Telethon fork — exactly as upstream uses it).

This pass focuses on **`pyUltroid/`** — the core framework — and intentionally
leaves the `plugins/`, `assistant/`, `vcbot/`, `addons/` trees untouched. All
public symbols those plugins import (`ultroid_cmd`, `asst_cmd`,
`inline_mention`, `eor`/`eod`, `UltroidClient`, `udB`, `LOGS`, …) keep their
existing signatures so existing plugins continue to work without changes.

> **Note on Telethon version.** Ultroid imports from `telethonpatch`, not
> `telethon`, so this refactor explicitly does **not** bump or swap the
> Telethon dependency. The deprecation/idiom fixes below (e.g.
> `asyncio.get_event_loop()` → `asyncio.create_task`) are the relevant
> "modernization" wins here; the Telethon surface area is otherwise stable.

---

## Files changed

| File | Why |
|------|-----|
| `pyUltroid/version.py` | Bumped to `2026.01.28` / `2.1.3`. |
| `pyUltroid/__init__.py` | Clean exits (`sys.exit(1)` not bare `exit()`), cache `OWNER_ID` once. |
| `pyUltroid/startup/__init__.py` | `int(v) < 10` → `sys.version_info < (3, 10)` (the original would have miscompared if Python ever bumped to 4.x). |
| `pyUltroid/startup/_extra.py` | `__builtins__["input"]` only worked from `__main__`; switched to `builtins.input = …`. |
| `pyUltroid/startup/BaseClient.py` | Major rewrite (see §1). |
| `pyUltroid/startup/connections.py` | Stopped calling `logger.exception` outside of an `except` block; localised-string fallback. |
| `pyUltroid/startup/_database.py` | Fixed SQL-injection, removed runtime `pip install` (see §2). |
| `pyUltroid/startup/loader.py` | Replaced every `subprocess.run(..., shell=True)` with list-form invocations. |
| `pyUltroid/fns/helper.py` | Many fixes (see §3). |
| `pyUltroid/_misc/__init__.py` | `_SudoManager.fullsudos` called `.get()` instead of `.get_key()`. Fixed + handles both string and list shapes. |
| `pyUltroid/_misc/_decorators.py` | Removed the disconnect/reconnect dance from the FloodWait handler — it was racy and broke other in-flight requests. |

---

## 1. `pyUltroid/startup/BaseClient.py`

* **Deleted the `__dict__` `@property`.** Returning `self.me.to_dict()` from
  `__dict__` corrupted instance attribute lookup and could prevent
  Telethon's internals from caching state. Several downstream
  "AttributeError on a client that should have the attribute" reports
  trace back to this.
* **`fast_uploader` / `fast_downloader`**: the `while not raw_file:` loop
  would spin forever if `upload_file`/`download_file` ever returned a
  falsy value. Now raises a clear `RuntimeError` instead. Progress
  callbacks switched from `self.loop.create_task(...)` to
  `asyncio.create_task(...)` (the former is brittle inside callbacks
  scheduled from foreign threads).
* **`start_client`**: tighter exit semantics — each error class is logged
  & exits cleanly without falling through to `await self.get_me()` after a
  failed login.
* **`add_handler`**: `any(existing is func ...)` instead of building a temp
  list with `[_[0] for _ in self.list_event_handlers()]` on every call.
* **Preserved** the `from telethonpatch import TelegramClient` import as-is
  — Ultroid relies on the patched client.

---

## 2. `pyUltroid/startup/_database.py`

* **Critical SQL fix.** `SqlDB.get`/`set`/`delete` interpolated user-supplied
  column names directly into SQL strings (`f"SELECT {variable} FROM Ultroid"`).
  Anything that ended up as a DB key — including DB keys derived from a
  Telegram message — could break out and execute arbitrary SQL. The whole
  class now uses `psycopg2.sql.Identifier`/`.Literal` composition, which is
  the documented safe way to parameterise identifiers in psycopg2.
* **Removed `os.system(f"{sys.executable} -m pip install …")` at import.**
  Auto-installing dependencies at runtime is brittle (network during boot)
  and confusing when it fails. We now raise `SystemExit(1)` with a clear
  `pip install …` hint instead.
* **Renamed `Database` → `LocalDatabase`** so it doesn't shadow other names
  in the module.
* **`__init__` types**: added consistent type hints across every backend.

---

## 3. `pyUltroid/fns/helper.py`

* **`inline_mention`** no longer shadows the stdlib `html` module — the
  parameter is now `as_html`, but the legacy `html=True` keyword is still
  accepted (via `**kwargs`) so existing plugins (`plugins/pmpermit.py`,
  etc.) keep working unchanged.
* **`progress`**: rewritten. The bar used `"".join("" for i in range(20-…))`,
  which always produced an empty string for the empty half of the bar, so
  the progress bar was actually invisible.
* **`run_async`**: uses one shared `ThreadPoolExecutor` instead of creating
  a fresh one (with `cpu_count()*5` threads!) on every call. Also switched
  from `asyncio.get_event_loop()` to `asyncio.get_running_loop()`.
* **`uploader` / `downloader`**: `asyncio.get_event_loop().create_task` →
  `asyncio.create_task` (the former emits a DeprecationWarning on 3.10+).
* **`gen_chlog`**: was calling `Repo()` inside the function while also
  receiving `repo` as an argument — the resolved upstream URL didn't match
  the repo we were diffing. Uses the passed repo throughout.
* **`updater`**: rewrote control flow. The previous version called
  `Repo().__del__()` on errors (manual `__del__` calls are basically never
  right) and recreated remotes inside an `if … else None` ternary just for
  side effects.
* **`restart`**: `sys.argv[1..6]` would `IndexError` if called with fewer
  than 6 CLI args. Uses `*sys.argv[1:]` instead.
* **`bash`**: regex `"\/bin\/sh: …"` is now a raw string so `\w` isn't
  treated as an unknown escape under Python 3.12+ (it currently emits a
  `DeprecationWarning`; in 3.13 it becomes a `SyntaxWarning`).
* **`humanbytes` / `numerize`**: simplified formatting; explicit
  `float(...)` conversion so callers passing strings don't silently
  produce nonsense.

---

## 4. `pyUltroid/_misc/_decorators.py`

The FloodWait handler used to do:

```python
await ultroid_bot.disconnect()
await asyncio.sleep(fwerr.seconds + 10)
await ultroid_bot.connect()
```

That's wrong on two counts:

1. `client.disconnect()` cancels every in-flight request, including ones
   queued by *other* handlers that aren't rate-limited — so a single
   FloodWait in one chat would silently fail every other request in
   flight.
2. Telethon already retries automatically after a FloodWait once you
   resume awaiting; you don't need to bounce the connection.

Now it just `await asyncio.sleep(wait)` in place and lets Telethon take it
from there.

---

## 5. `pyUltroid/startup/loader.py`

Replaced every `subprocess.run("some f-string", shell=True)` with list-form
`subprocess.run(["git", "clone", …])`. Concretely:

* `ADDONS_URL` was concatenated into a shell command. A user-controlled
  Redis key could therefore execute arbitrary shell on the host.
* `Repo().active_branch` was interpolated without quoting; if the active
  branch name ever contained whitespace, the clone would silently break.
* `cd vcbot && git pull` and `cd addons && git pull && cd ..` are now
  `git -C vcbot pull` / `git -C addons pull -q`.

---

## 6. What was intentionally **not** changed

* **`pyUltroid/fns/FastTelethon.py`** — vendored from `mautrix-telegram`
  and works fine against `telethonpatch`.
* **`plugins/*.py`, `assistant/*.py`, `vcbot/*.py`, `addons/*`** — out of
  scope for "core code". Each is its own surface area and should be
  iterated on individually.
* **`pyUltroid/startup/funcs.py` `autobot` / `customize` / `autopilot`** —
  the BotFather conversation flow there is fragile, but reworking it
  requires a working bot token to test against. Left as-is.
* **`requirements.txt`** — Ultroid pulls a custom Telethon fork via
  `https://github.com/New-dev0/Telethon-Patch/archive/main.zip`. Touching
  that is a separate decision; nothing in this refactor depends on it.

---

## 7. How to apply

```bash
git checkout -b refactor/core-modernization
git am < ultroid_refactor.patch
python3 -m pyUltroid                       # exactly as before
```

---

## 8. Suggested follow-ups (out of scope)

1. Switch `pyUltroid/configs.Var` to `pydantic-settings` for proper
   validation (the current `decouple.config` defaults silently hide
   misconfigured envs).
2. Add a smoke-test that imports every plugin without starting the bot.
3. Replace the brittle BotFather scraping in `autobot()` with proper
   waited conversations (`async with client.conversation(...)` already
   exists in Telethon for exactly this).
4. Pin `telethonpatch` to a specific commit instead of `archive/main.zip`
   — your CI is otherwise non-reproducible.
