# Contributing to Ultroid

Thanks for helping improve Ultroid. Any contribution is appreciated.

## About

- **Ultroid** is a Telethon-based Telegram userbot.
- Core runtime lives in-tree under `pyUltroid/` (also published historically as a pip package).
- Official plugins: `plugins/`, assistant: `assistant/`.
- Extra community plugins: [UltroidAddons](https://github.com/TeamUltroid/UltroidAddons).

## Local development

```bash
git clone https://github.com/TeamUltroid/Ultroid.git
cd Ultroid
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-db-redis.txt   # or mongo/postgres
# optional plugin extras:
# pip install -r requirements-full.txt

cp .env.sample .env   # or: python -m pyUltroid setup
bash sessiongen       # fill SESSION in .env
python -m pyUltroid doctor
bash startup
```

Docker (app + Redis):

```bash
cp .env.sample .env   # set API_ID, API_HASH, SESSION
docker compose up -d --build
```

## Project layout

| Path | Role |
|------|------|
| `pyUltroid/` | Core client, DB, loader, startup |
| `plugins/` | Official userbot commands |
| `assistant/` | BotFather assistant + callbacks |
| `strings/` | i18n YAML (`en.yml` is source of truth) |
| `tests/` | Unit tests (no Telegram network) |

## Plugin tips

- Use `@ultroid_cmd(pattern="...")` from `plugins/__init__.py` imports.
- Document with `__doc__ = get_help("help_yourplugin")` and add keys under `strings/strings/en.yml`.
- Prefer specific exceptions over bare `except:`.
- Known DB keys can be listed with `.keys`; typed keys are validated in `setdb` via `pyUltroid/startup/settings_schema.py`.

## Checks before a PR

```bash
python -m unittest discover -s tests -v
python -m pyUltroid doctor
```

- Keep diffs focused; avoid drive-by refactors.
- Do not commit `.env`, sessions, or secrets.
- Reference related issues in the PR body.

## Issues

- Search for existing similar issues first.
- Open an issue before large feature work when possible.

## Pull requests

1. Fork and branch from `main` (or the target preview branch).
2. Commit with a clear message.
3. Open a PR with a short summary of *why* and *what*.
4. Ensure CI smoke tests pass.

## Thanks

You are helping keep Ultroid usable for everyone — thank you.
