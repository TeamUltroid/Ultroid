# Glossary

Ultroid's terms, what they mean, and the name each one takes in Rust, so every unit names the same
thing the same way. A Rust name is filled in when the first unit that needs the term is ported.

| Term | Meaning | In Rust |
| --- | --- | --- |
| `udB` | The key-value database every part of Ultroid reads and writes. One of Redis, MongoDB, PostgreSQL or a local JSON file, behind `get_key`, `set_key`, `del_key`, `keys`. | not ported yet |
| stored value | What `set_key` writes: `str(value)`. `get_key` reads it back with `ast.literal_eval` and keeps the raw string when that fails. | not ported yet |
| `HNDLR` | The command prefix for the owner's own commands. Default `.`. | not ported yet |
| `SUDO_HNDLR`, `DUAL_HNDLR` | The prefixes for sudo users and for the assistant in dual mode. | not ported yet |
| pattern | The regular expression a plugin registers for a command, without the prefix. | not ported yet |
| `ultroid_bot` | The user account client. | blocked (ADR-005) |
| `asst` | The assistant: the bot account client. | blocked (ADR-005) |
| plugin | A Python file in `plugins/` whose handlers are registered on import. | blocked (ADR-006) |
| addon | A plugin from the UltroidAddons repository or installed from chat at runtime. | blocked (ADR-006) |
| sudo user, full sudo | Users allowed to run the owner's commands; full sudo may run the dangerous ones. | not ported yet |
| language | A file in `strings/strings/<code>.yml`. `get_string(key)` reads the current language and falls back to English. | not ported yet |
| session string | The login credential for the user account: a Telethon string, or a Pyrogram string converted on start. | not ported yet |
| client number | `1` to `5`: the suffix that selects one client's variables in `multi_client.py`. | not ported yet |
