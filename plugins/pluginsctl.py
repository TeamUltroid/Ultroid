# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# Official plugin enable/disable helpers and a dev-oriented reload.

"""Manage which official plugins load on boot, and reload addons in-session."""

import os
from pathlib import Path

from pyUltroid.startup.loader import load_addons

from . import LOGS, eor, get_string, udB, ultroid_cmd, un_plug

_PLUGINS_DIR = Path("plugins")


def _official_names():
    return sorted(
        p.stem
        for p in _PLUGINS_DIR.glob("*.py")
        if not p.name.startswith("_") and p.stem not in {"pluginsctl"}
    )


def _split_list(val):
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x) for x in val]
    return str(val).split()


def _join_list(items):
    return " ".join(sorted(set(items)))


@ultroid_cmd(pattern="plugins$", fullsudo=True)
async def list_plugins(event):
    """List official plugins and current exclude/include filters."""
    names = _official_names()
    exclude = _split_list(udB.get_key("EXCLUDE_OFFICIAL"))
    include = _split_list(udB.get_key("INCLUDE_ONLY"))
    lines = [
        f"**Official plugins on disk:** `{len(names)}`",
        f"**EXCLUDE_OFFICIAL:** `{_join_list(exclude) or '—'}`",
        f"**INCLUDE_ONLY:** `{_join_list(include) or '—'}`",
        "",
        "Toggle: `.disableplugin name` · `.enableplugin name`",
        "Dev reload (addons): `.reload name`",
        "Restart required for official enable/disable to fully apply.",
    ]
    # show a short sample of disabled
    if exclude:
        lines.append("\n**Disabled (sample):** " + ", ".join(f"`{x}`" for x in exclude[:15]))
    await event.eor("\n".join(lines))


@ultroid_cmd(pattern="disableplugin( (.*)|$)", fullsudo=True)
async def disable_plugin(event):
    name = event.pattern_match.group(1).strip().removesuffix(".py")
    if not name:
        return await event.eor("Usage: `.disableplugin <official_plugin>`")
    if name.startswith("_"):
        return await event.eor("Internal plugins (starting with `_`) can't be toggled.")
    path = _PLUGINS_DIR / f"{name}.py"
    if not path.exists():
        return await event.eor(f"`{name}` is not an official plugin.")
    exclude = _split_list(udB.get_key("EXCLUDE_OFFICIAL"))
    if name not in exclude:
        exclude.append(name)
    udB.set_key("EXCLUDE_OFFICIAL", _join_list(exclude))
    # Also drop from INCLUDE_ONLY if present
    include = _split_list(udB.get_key("INCLUDE_ONLY"))
    if name in include:
        include = [x for x in include if x != name]
        if include:
            udB.set_key("INCLUDE_ONLY", _join_list(include))
        else:
            udB.del_key("INCLUDE_ONLY")
    await event.eor(
        f"**Disabled** `{name}` (EXCLUDE_OFFICIAL).\n"
        f"Restart with `.restart` to unload it from this session."
    )


@ultroid_cmd(pattern="enableplugin( (.*)|$)", fullsudo=True)
async def enable_plugin(event):
    name = event.pattern_match.group(1).strip().removesuffix(".py")
    if not name:
        return await event.eor("Usage: `.enableplugin <official_plugin>`")
    exclude = _split_list(udB.get_key("EXCLUDE_OFFICIAL"))
    if name in exclude:
        exclude = [x for x in exclude if x != name]
        if exclude:
            udB.set_key("EXCLUDE_OFFICIAL", _join_list(exclude))
        else:
            udB.del_key("EXCLUDE_OFFICIAL")
    await event.eor(
        f"**Enabled** `{name}`.\nRestart with `.restart` so it loads on boot."
    )


@ultroid_cmd(pattern="reload( (.*)|$)", fullsudo=True)
async def reload_plugin(event):
    """Reload an unofficial/addon plugin without full restart (dev helper)."""
    name = event.pattern_match.group(1).strip().removesuffix(".py")
    if not name:
        return await event.eor("Usage: `.reload <addon_plugin>`")
    addon_path = Path("addons") / f"{name}.py"
    official_path = _PLUGINS_DIR / f"{name}.py"
    if official_path.exists() and not addon_path.exists():
        return await event.eor(
            "Official plugins can't hot-reload safely — use "
            "`.disableplugin` / `.enableplugin` + `.restart`."
        )
    if not addon_path.exists():
        return await event.eor(f"No addon named `{name}` in addons/.")
    try:
        try:
            un_plug(name)
        except Exception:
            pass
        load_addons(str(addon_path))
        await event.eor(f"**Reloaded** addon `{name}`.")
    except Exception as er:
        LOGS.exception(er)
        await event.eor(f"Reload failed: `{er}`")
