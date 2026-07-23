# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""Health check: versions, disk, DB ping summary, last plugin load report."""

import os
import platform
import shutil
from io import StringIO

from pyUltroid.loader import LOAD_REPORT
from pyUltroid.version import __version__ as pyult_ver
from pyUltroid.version import ultroid_version

from . import HOSTED_ON, LOGS, eor, udB, ultroid_cmd


def _build_report() -> str:
    lines = [
        "**Ultroid doctor**",
        f"• Ultroid `{ultroid_version}` · pyUltroid `{pyult_ver}`",
        f"• Python `{platform.python_version()}`",
        f"• Host `{HOSTED_ON}`",
    ]
    try:
        usage = shutil.disk_usage(".")
        lines.append(
            f"• Disk `{usage.free // (1024 * 1024)} MB` free / "
            f"`{usage.total // (1024 * 1024)} MB` total"
        )
    except Exception:
        pass
    lines.append(f"• DB `{getattr(udB, 'name', '?')}`")
    try:
        if udB.ping():
            lines.append("• DB ping `ok`")
        else:
            lines.append("• DB ping `failed`")
    except Exception as er:
        lines.append(f"• DB ping `error: {er}`")

    loaded = LOAD_REPORT.get("loaded") or []
    missing = LOAD_REPORT.get("skipped_missing_dep") or []
    failed = LOAD_REPORT.get("failed") or []
    lines.append(
        f"• Plugins loaded `{len(loaded)}` · missing-dep `{len(missing)}` · failed `{len(failed)}`"
    )
    if missing:
        lines.append("**Missing deps (sample):**")
        for group, name, dep in missing[:8]:
            lines.append(f"  `{group}/{name}` → `{dep}`")
        if len(missing) > 8:
            lines.append(f"  … +{len(missing) - 8} more")
    if failed:
        lines.append("**Failed (sample):**")
        for group, name, reason in failed[:5]:
            short = reason.splitlines()[0][:80]
            lines.append(f"  `{group}/{name}`: `{short}`")
    lines.append(
        "\nCLI: `python -m pyUltroid doctor` on the host for full package/DB probes."
    )
    return "\n".join(lines)


@ultroid_cmd(pattern="doctor$", fullsudo=True)
async def doctor_cmd(event):
    msg = await event.eor("`Running doctor…`")
    try:
        text = _build_report()
    except Exception as er:
        LOGS.exception(er)
        return await msg.edit(f"`doctor failed: {er}`")
    if len(text) > 3900:
        text = text[:3900] + "\n…"
    await msg.edit(text)
