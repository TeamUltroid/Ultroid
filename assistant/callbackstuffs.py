# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import ast
import asyncio
import re
import sys
import time
from asyncio.exceptions import TimeoutError as AsyncTimeOut
from os import execl, remove
from random import choice

from bs4 import BeautifulSoup as bs

try:
    from pyUltroid.fns.gDrive import GDriveManager
except ImportError:
    GDriveManager = None
from telethon import Button, events
from catbox import CatboxUploader
from telethon.tl.types import MessageMediaWebPage
from telethon.utils import get_peer_id

from pyUltroid.fns.helper import fast_download, progress
from pyUltroid.fns.tools import Carbon, async_searcher, get_paste, telegraph_client
from pyUltroid.startup.loader import Loader

from . import *

telegraph = telegraph_client()
GDrive = GDriveManager() if GDriveManager else None
uploader = CatboxUploader()

def text_to_url(event):
    if isinstance(event.media, MessageMediaWebPage):
        webpage = event.media.webpage
        if not isinstance(webpage, types.WebPageEmpty) and webpage.type in ["photo"]:
            return webpage.display_url
    return event.text

_buttons = {
    "otvars": {
        "text": "⚙️ 𝖮𝗍𝗁𝖾𝗋 𝖵𝖺𝗋𝗂𝖺𝖻𝗅𝖾𝗌 𝗍𝗈 𝗌𝖾𝗍 𝖿𝗈𝗋 @TeamUltroid:",
        "buttons": [
            [Button.inline("🏷️ 𝖳𝖺𝗀 𝖫𝗈𝗀𝗀𝖾𝗋", data="taglog"), Button.inline("🛡️ 𝖲𝗎𝗉𝖾𝗋𝖥𝖡𝖺𝗇", data="cbs_sfban")],
            [Button.inline("👤 𝖲𝗎𝖽𝗈 𝖬𝗈𝖽𝖾", data="sudo"), Button.inline("⚡ 𝖧𝖺𝗇𝖽𝗅𝖾𝗋", data="hhndlr")],
            [Button.inline("🧩 𝖤𝗑𝗍𝗋𝖺 𝖯𝗅𝗎𝗀𝗂𝗇𝗌", data="plg"), Button.inline("📦 𝖠𝖽𝖽𝗈𝗇𝗌", data="eaddon")],
            [Button.inline("😀 𝖤𝗆𝗈𝗃𝗂 𝗂𝗇 𝖧𝖾𝗅𝗉", data="emoj"), Button.inline("☁️ 𝖲𝖾𝗍 𝗀𝖣𝗋𝗂𝗏𝖾", data="gdrive")],
            [Button.inline("🖼️ 𝖨𝗇𝗅𝗂𝗇𝖾 𝖯𝗂𝖼", data="inli_pic"), Button.inline("👑 𝖲𝗎𝖽𝗈 𝖧𝖭𝖣𝖫𝖱", data="shndlr")],
            [Button.inline("🌗 𝖣𝗎𝖺𝗅 𝖬𝗈𝖽𝖾", "cbs_oofdm")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="setter")],
        ],
    },
    "sfban": {
        "text": "🛡️ 𝖲𝗎𝗉𝖾𝗋𝖥𝖡𝖺𝗇 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌:",
        "buttons": [
            [Button.inline("👥 𝖥𝖡𝖺𝗇 𝖦𝗋𝗈𝗎𝗉", data="sfgrp")],
            [Button.inline("🚫 𝖤𝗑𝖼𝗅𝗎𝖽𝖾 𝖥𝖾𝖽𝗌", data="abs_sfexf")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_otvars")],
        ],
    },
    "apauto": {
        "text": "✅ 𝖳𝗁𝗂𝗌 𝗐𝗂𝗅𝗅 𝖺𝗎𝗍𝗈-𝖺𝗉𝗉𝗋𝗈𝗏𝖾 𝗈𝗇 𝗈𝗎𝗍𝗀𝗈𝗂𝗇𝗀 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌.",
        "buttons": [
            [Button.inline("🟢 𝖠𝗎𝗍𝗈 𝖠𝗉𝗉𝗋𝗈𝗏𝖾 𝖮𝖭", data="apon")],
            [Button.inline("🔴 𝖠𝗎𝗍𝗈 𝖠𝗉𝗉𝗋𝗈𝗏𝖾 𝖮𝖥𝖥", data="apof")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_pmcstm")],
        ],
    },
    "alvcstm": {
        "text": f"✨ 𝖢𝗎𝗌𝗍𝗈𝗆𝗂𝗌𝖾 𝗒𝗈𝗎𝗋 `{HNDLR}alive`. 𝖢𝗁𝗈𝗈𝗌𝖾 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝗈𝗉𝗍𝗂𝗈𝗇𝗌 𝖻𝖾𝗅𝗈𝗐:",
        "buttons": [
            [Button.inline("📝 𝖠𝗅𝗂𝗏𝖾 𝖳𝖾𝗑𝗍", data="abs_alvtx")],
            [Button.inline("🖼️ 𝖠𝗅𝗂𝗏𝖾 𝖬𝖾𝖽𝗂𝖺", data="alvmed")],
            [Button.inline("🗑️ 𝖣𝖾𝗅𝖾𝗍𝖾 𝖠𝗅𝗂𝗏𝖾 𝖬𝖾𝖽𝗂𝖺", data="delmed")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="setter")],
        ],
    },
    "pmcstm": {
        "text": "⚙️ 𝖢𝗎𝗌𝗍𝗈𝗆𝗂𝗌𝖾 𝗒𝗈𝗎𝗋 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌:",
        "buttons": [
            [Button.inline("📝 𝖯𝖬 𝖳𝖾𝗑𝗍", data="pmtxt"), Button.inline("🖼️ 𝖯𝖬 𝖬𝖾𝖽𝗂𝖺", data="pmmed")],
            [Button.inline("✅ 𝖠𝗎𝗍𝗈 𝖠𝗉𝗉𝗋𝗈𝗏𝖾", data="cbs_apauto"), Button.inline("🗂️ 𝖯𝖬 𝖫𝗈𝗀𝗀𝖾𝗋", data="pml")],
            [Button.inline("⚠️ 𝖲𝖾𝗍 𝖶𝖺𝗋𝗇𝗌", data="swarn"), Button.inline("🗑️ 𝖣𝖾𝗅𝖾𝗍𝖾 𝖯𝖬 𝖬𝖾𝖽𝗂𝖺", data="delpmmed")],
            [Button.inline("🎛️ 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝖳𝗒𝗉𝖾", data="cbs_pmtype")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_ppmset")],
        ],
    },
    "pmtype": {
        "text": "🎛️ 𝖲𝖾𝗅𝖾𝖼𝗍 𝗍𝗁𝖾 𝗍𝗒𝗉𝖾 𝗈𝖿 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝗇𝖾𝖾𝖽𝖾𝖽:",
        "buttons": [
            [Button.inline("🔘 𝖨𝗇𝗅𝗂𝗇𝖾", data="inpm_in")],
            [Button.inline("🔘 𝖭𝗈𝗋𝗆𝖺𝗅", data="inpm_no")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_pmcstm")],
        ],
    },
    "ppmset": {
        "text": "🛡️ 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌:",
        "buttons": [
            [Button.inline("🟢 𝖳𝗎𝗋𝗇 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝖮𝖭", data="pmon")],
            [Button.inline("🔴 𝖳𝗎𝗋𝗇 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝖮𝖥𝖥", data="pmoff")],
            [Button.inline("⚙️ 𝖢𝗎𝗌𝗍𝗈𝗆𝗂𝗓𝖾 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍", data="cbs_pmcstm")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="setter")],
        ],
    },
    "chatbot": {
        "text": "🤖 𝖥𝗋𝗈𝗆 𝗍𝗁𝗂𝗌 𝖿𝖾𝖺𝗍𝗎𝗋𝖾, 𝗒𝗈𝗎 𝖼𝖺𝗇 𝖼𝗁𝖺𝗍 𝗐𝗂𝗍𝗁 𝗉𝖾𝗈𝗉𝗅𝖾 𝗏𝗂𝖺 𝗒𝗈𝗎𝗋 𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍 𝖡𝗈𝗍.\n[ℹ️ 𝖬𝗈𝗋𝖾 𝖨𝗇𝖿𝗈](https://t.me/UltroidUpdates/2)",
        "buttons": [
            [Button.inline("🟢 𝖢𝗁𝖺𝗍 𝖡𝗈𝗍 𝖮𝖭", data="onchbot"), Button.inline("🔴 𝖢𝗁𝖺𝗍 𝖡𝗈𝗍 𝖮𝖥𝖥", data="ofchbot")],
            [Button.inline("👋 𝖡𝗈𝗍 𝖶𝖾𝗅𝖼𝗈𝗆𝖾", data="bwel"), Button.inline("🖼️ 𝖡𝗈𝗍 𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝖬𝖾𝖽𝗂𝖺", data="botmew")],
            [Button.inline("ℹ️ 𝖡𝗈𝗍 𝖨𝗇𝖿𝗈 𝖳𝖾𝗑𝗍", data="botinfe")],
            [Button.inline("📢 𝖥𝗈𝗋𝖼𝖾 𝖲𝗎𝖻𝗌𝖼𝗋𝗂𝖻𝖾", data="pmfs")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="setter")],
        ],
    },
    "vcb": {
        "text": "🎵 𝖥𝗋𝗈𝗆 𝗍𝗁𝗂𝗌 𝖿𝖾𝖺𝗍𝗎𝗋𝖾, 𝗒𝗈𝗎 𝖼𝖺𝗇 𝗉𝗅𝖺𝗒 𝗌𝗈𝗇𝗀𝗌 𝗂𝗇 𝗀𝗋𝗈𝗎𝗉 𝗏𝗈𝗂𝖼𝖾 𝖼𝗁𝖺𝗍𝗌.\n[ℹ️ 𝖬𝗈𝗋𝖾 𝖨𝗇𝖿𝗈](https://t.me/UltroidUpdates/4)",
        "buttons": [
            [Button.inline("🎙️ 𝖵𝖢 𝖲𝖾𝗌𝗌𝗂𝗈𝗇", data="abs_vcs")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="setter")],
        ],
    },
    "oofdm": {
        "text": "🌗 𝖠𝖻𝗈𝗎𝗍 [𝖣𝗎𝖺𝗅 𝖬𝗈𝖽𝖾](https://t.me/UltroidUpdates/18)",
        "buttons": [
            [Button.inline("🟢 𝖣𝗎𝖺𝗅 𝖬𝗈𝖽𝖾 𝖮𝖭", "dmof"), Button.inline("🔴 𝖣𝗎𝖺𝗅 𝖬𝗈𝖽𝖾 𝖮𝖥𝖥", "dmof")],
            [Button.inline("⚡ 𝖣𝗎𝖺𝗅 𝖬𝗈𝖽𝖾 𝖧𝖭𝖣𝖫𝖱", "dmhn")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_otvars")],
        ],
    },
    "apiset": {
        "text": get_string("ast_1"),
        "buttons": [
            [Button.inline("✂️ Remove.bg API", data="abs_rmbg")],
            [Button.inline("🧠 DEEP API", data="abs_dapi")],
            [Button.inline("🔤 OCR API", data="abs_oapi")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="setter")],
        ],
    },
}

_convo = {
    "rmbg": {"var": "RMBG_API", "name": "Remove.bg API Key", "text": get_string("ast_2"), "back": "cbs_apiset"},
    "dapi": {"var": "DEEP_AI", "name": "Deep AI Api Key", "text": "🤖 𝖦𝖾𝗍 𝗒𝗈𝗎𝗋 𝖣𝖾𝖾𝗉 𝖠𝖨 𝖠𝖯𝖨 𝖿𝗋𝗈𝗆 𝖽𝖾𝖾𝗉𝖺𝗂.𝗈𝗋𝗀 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗂𝗍 𝗁𝖾𝗋𝖾.", "back": "cbs_apiset"},
    "oapi": {"var": "OCR_API", "name": "Ocr Api Key", "text": "🔤 𝖦𝖾𝗍 𝗒𝗈𝗎𝗋 𝖮𝖢𝖱 𝖠𝖯𝖨 𝖿𝗋𝗈𝗆 𝗈𝖼𝗋.𝗌𝗉𝖺𝖼𝖾 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗂𝗍 𝗁𝖾𝗋𝖾.", "back": "cbs_apiset"},
    "pmlgg": {"var": "PMLOGGROUP", "name": "Pm Log Group", "text": "🗂️ 𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝖢𝗁𝖺𝗍 𝖨𝖣 𝗈𝖿 𝗍𝗁𝖾 𝖼𝗁𝖺𝗍 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗌𝖺𝗏𝖾 𝖺𝗌 𝖯𝖬 𝖫𝗈𝗀 𝖦𝗋𝗈𝗎𝗉.", "back": "pml"},
    "vcs": {"var": "VC_SESSION", "name": "Vc Session", "text": "🎙️ **𝖵𝖢 𝖲𝖾𝗌𝗌𝗂𝗈𝗇**\n𝖤𝗇𝗍𝖾𝗋 𝗍𝗁𝖾 𝗇𝖾𝗐 𝗌𝖾𝗌𝗌𝗂𝗈𝗇 𝗒𝗈𝗎 𝗀𝖾𝗇𝖾𝗋𝖺𝗍𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝖾 𝖵𝖢 𝖻𝗈𝗍.\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝗍𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾.*", "back": "cbs_vcb"},
    "settag": {"var": "TAG_LOG", "name": "Tag Log Group", "text": f"🏷️ 𝖬𝖺𝗄𝖾 𝖺 𝗀𝗋𝗈𝗎𝗉, 𝖺𝖽𝖽 𝗒𝗈𝗎𝗋 𝖺𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍 𝖺𝗇𝖽 𝗆𝖺𝗄𝖾 𝗂𝗍 𝖺𝖽𝗆𝗂𝗇.\n𝖦𝖾𝗍 𝗍𝗁𝖾 `{HNDLR}id` 𝗈𝖿 𝗍𝗁𝖺𝗍 𝗀𝗋𝗈𝗎𝗉 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗂𝗍 𝗁𝖾𝗋𝖾 𝖿𝗈𝗋 𝗍𝖺𝗀 𝗅𝗈𝗀𝗌.\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝖼𝖺𝗇𝖼𝖾𝗅.*", "back": "taglog"},
    "alvtx": {"var": "ALIVE_TEXT", "name": "Alive Text", "text": "📝 **𝖠𝗅𝗂𝗏𝖾 𝖳𝖾𝗑𝗍**\n𝖤𝗇𝗍𝖾𝗋 𝗍𝗁𝖾 𝗇𝖾𝗐 𝖺𝗅𝗂𝗏𝖾 𝗍𝖾𝗑𝗍.\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝗍𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾.*", "back": "cbs_alvcstm"},
    "sfexf": {"var": "EXCLUDE_FED", "name": "Excluded Fed", "text": "🚫 𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝖥𝖾𝖽 𝖨𝖣𝗌 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝖾𝗑𝖼𝗅𝗎𝖽𝖾 𝗂𝗇 𝗍𝗁𝖾 𝖻𝖺𝗇. 𝖲𝗉𝗅𝗂𝗍 𝖻𝗒 𝖺 𝗌𝗉𝖺𝖼𝖾.\n𝖤.𝗀. `id1 id2 id3`\n𝖲𝖾𝗍 𝗂𝗍 𝖺𝗌 `None` 𝗂𝖿 𝗒𝗈𝗎 𝖽𝗈𝗇'𝗍 𝗐𝖺𝗇𝗍 𝖺𝗇𝗒.\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝗀𝗈 𝖻𝖺𝖼𝗄.*", "back": "cbs_sfban"},
}

TOKEN_FILE = "resources/auths/auth_token.txt"

@callback(re.compile("sndplug_(.*)"), owner=True)
async def send(eve):
    key, name = (eve.data_match.group(1)).decode("UTF-8").split("_")
    thumb = "resources/extras/inline.jpg"
    await eve.answer("🚀 𝖲𝖾𝗇𝖽𝗂𝗇𝗀...")
    index = None
    if "|" in name:
        name, index = name.split("|")
    key = "plugins" if key == "Official" else key.lower()
    plugin = f"{key}/{name}.py"
    _ = f"pasta-{plugin}"
    data = f"uh_{key}_"
    if index is not None:
        data += f"|{index}"
        _ += f"|{index}"
    buttons = [
        [Button.inline("« 𝖯𝖺𝗌𝗍𝖾 »", data=_)],
        [Button.inline("« 𝖡𝖺𝖼𝗄", data=data)],
    ]
    try:
        await eve.edit(file=plugin, thumb=thumb, buttons=buttons)
    except Exception as er:
        await eve.answer(str(er), alert=True)

heroku_api, app_name = Var.HEROKU_API, Var.HEROKU_APP_NAME

@callback("updatenow", owner=True)
async def update(eve):
    repo = Repo()
    ac_br = repo.active_branch
    ups_rem = repo.remote("upstream")
    if heroku_api:
        import heroku3
        try:
            heroku = heroku3.from_key(heroku_api)
            heroku_app = next((app for app in heroku.apps() if app.name == app_name), None)
        except BaseException as er:
            LOGS.exception(er)
            return await eve.edit("`❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖧𝖤𝖱𝖮𝖪𝖴_𝖠𝖯𝖨.`")
        if not heroku_app:
            await eve.edit("`❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖧𝖤𝖱𝖮𝖪𝖴_𝖠𝖯𝖯_𝖭𝖠𝖬𝖤.`")
            return repo.__del__()
        await eve.edit(get_string("clst_1"))
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace("https://", f"https://api:{heroku_api}@")
        remote = repo.remote("heroku") if "heroku" in repo.remotes else repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        except GitCommandError as error:
            await eve.edit(f"`⚠️ 𝖤𝗋𝗋𝗈𝗋 𝖫𝗈𝗀:\n{error}`")
            return repo.__del__()
        await eve.edit("`✅ 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝖴𝗉𝖽𝖺𝗍𝖾𝖽!\n🔄 𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝗂𝗇𝗀, 𝗉𝗅𝖾𝖺𝗌𝖾 𝗐𝖺𝗂𝗍...`")
    else:
        await eve.edit(get_string("clst_1"))
        call_back()
        await bash("git pull && pip3 install -r requirements.txt --break-system-packages")
        execl(sys.executable, sys.executable, "-m", "pyUltroid")

@callback(re.compile("changes(.*)"), owner=True)
async def changes(okk):
    match = okk.data_match.group(1).decode("utf-8")
    await okk.answer(get_string("clst_3"))
    repo = Repo.init()
    button = [[Button.inline("🔄 𝖴𝗉𝖽𝖺𝗍𝖾 𝖭𝗈𝗐", data="updatenow")]]
    changelog, tl_chnglog = await gen_chlog(repo, f"HEAD..upstream/{repo.active_branch}")
    cli = "\n\n👇 𝖢𝗅𝗂𝖼𝗄 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝗎𝗉𝖽𝖺𝗍𝖾!"
    if not match:
        try:
            if len(tl_chnglog) > 700:
                tl_chnglog = f"{tl_chnglog[:700]}..."
                button.append([Button.inline("📄 𝖵𝗂𝖾𝗐 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝖾", "changesall")])
            await okk.edit("• 𝖶𝗋𝗂𝗍𝗂𝗇𝗀 𝖢𝗁𝖺𝗇𝗀𝖾𝗅𝗈𝗀𝗌 📝 •")
            img = await Carbon(file_name="changelog", code=tl_chnglog, backgroundColor=choice(ATRA_COL), language="md")
            return await okk.edit(f"**• 𝙐𝙡𝙩𝙧𝙤𝙞𝙙 𝙐𝙨𝙚𝙧𝙗𝙤𝙩 •**{cli}", file=img, buttons=button)
        except Exception as er:
            LOGS.exception(er)
    changelog_str = changelog + cli
    if len(changelog_str) > 1024:
        await okk.edit(get_string("upd_4"))
        await asyncio.sleep(2)
        with open("ultroid_updates.txt", "w+") as file:
            file.write(tl_chnglog)
        await okk.edit(get_string("upd_5"), file="ultroid_updates.txt", buttons=button)
        remove("ultroid_updates.txt")
        return
    await okk.edit(changelog_str, buttons=button, parse_mode="html")

@callback(re.compile("pasta-(.*)"), owner=True)
async def _(e):
    ok = (e.data_match.group(1)).decode("UTF-8")
    index = None
    if "|" in ok:
        ok, index = ok.split("|")
    with open(ok, "r") as hmm:
        _, data = await get_paste(hmm.read())
    key = ok
    if not data.get("link"):
        return await e.answer(key[:30], alert=True)
    link, raw = (data["link"], data["raw"]) if not key.startswith("http") else (key, f"{key}/raw")
    key_name = "Addons" if ok.startswith("addons") else "VCBot" if ok.startswith("vcbot") else "Official"
    data_btn = f"uh_{key_name}_" + (f"|{index}" if index is not None else "")
    await e.edit("", buttons=[
        [Button.url("🔗 𝖫𝗂𝗇𝗄", link), Button.url("📄 𝖱𝖺𝗐", raw)],
        [Button.inline("« 𝖡𝖺𝖼𝗄", data=data_btn)],
    ])

@callback(re.compile("cbs_(.*)"), owner=True)
async def _edit_to(event):
    if data := _buttons.get(event.data_match.group(1).decode("utf-8")):
        await event.edit(data["text"], buttons=data["buttons"], link_preview=False)

@callback(re.compile("abs_(.*)"), owner=True)
async def convo_handler(event: events.CallbackQuery):
    if not (get_ := _convo.get(event.data_match.group(1).decode("utf-8"))):
        return
    await event.delete()
    back = get_["back"]
    async with event.client.conversation(event.sender_id) as conv:
        await conv.send_message(get_["text"])
        response = await conv.get_response()
        themssg = response.message
        try:
            themssg = ast.literal_eval(themssg)
        except Exception:
            pass
        if themssg == "/cancel":
            return await conv.send_message("🚫 𝖮𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button(back))
        await setit(event, get_["var"], themssg)
        await conv.send_message(f"✅ **{get_['name']}** 𝖼𝗁𝖺𝗇𝗀𝖾𝖽 𝗍𝗈 `{themssg}`", buttons=get_back_button(back))

@callback("authorise", owner=True)
async def _(e):
    if not e.is_private:
        return
    url = GDrive._create_token_file()
    await e.edit("🌐 𝖦𝗈 𝗍𝗈 𝗍𝗁𝖾 𝗅𝗂𝗇𝗄 𝖻𝖾𝗅𝗈𝗐 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗍𝗁𝖾 𝖼𝗈𝖽𝖾!")
    async with asst.conversation(e.sender_id) as conv:
        await conv.send_message(url)
        code = await conv.get_response()
        if GDrive._create_token_file(code=code.text):
            await conv.send_message("✅ **𝖲𝗎𝖼𝖼𝖾𝗌𝗌!**\n𝖸𝗈𝗎 𝖺𝗋𝖾 𝖺𝗅𝗅 𝗌𝖾𝗍 𝗍𝗈 𝗎𝗌𝖾 𝖦𝗈𝗈𝗀𝗅𝖾 𝖣𝗋𝗂𝗏𝖾 𝗐𝗂𝗍𝗁 𝙐𝙡𝙩𝙧𝙤𝙞𝙙.", buttons=Button.inline("🏠 𝖬𝖺𝗂𝗇 𝖬𝖾𝗇𝗎", data="setter"))
        else:
            await conv.send_message("❌ 𝖶𝗋𝗈𝗇𝗀 𝖼𝗈𝖽𝖾! 𝖢𝗅𝗂𝖼𝗄 𝖺𝗎𝗍𝗁𝗈𝗋𝗂𝗌𝖾 𝖺𝗀𝖺𝗂𝗇.")

@callback("folderid", owner=True, func=lambda x: x.is_private)
async def _(e):
    if not e.is_private:
        return
    msg = "📁 **𝖲𝖾𝗇𝖽 𝗒𝗈𝗎𝗋 𝖥𝖮𝖫𝖣𝖤𝖱 𝖨𝖣**\n\n1. 𝖮𝗉𝖾𝗇 𝖦𝗈𝗈𝗀𝗅𝖾 𝖣𝗋𝗂𝗏𝖾 𝖠𝗉𝗉.\n2. 𝖢𝗋𝖾𝖺𝗍𝖾 𝖺 𝖥𝗈𝗅𝖽𝖾𝗋.\n3. 𝖬𝖺𝗄𝖾 𝗍𝗁𝖺𝗍 𝖿𝗈𝗅𝖽𝖾𝗋 𝗉𝗎𝖻𝗅𝗂𝖼.\n4. 𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝗅𝗂𝗇𝗄 𝗈𝖿 𝗍𝗁𝖺𝗍 𝖿𝗈𝗅𝖽𝖾𝗋."
    await e.delete()
    async with asst.conversation(e.sender_id, timeout=150) as conv:
        await conv.send_message(msg)
        repl = await conv.get_response()
        id = repl.text.split("?id=")[-1] if repl.text.startswith("https") else repl.text
        udB.set_key("GDRIVE_FOLDER_ID", id)
        await repl.reply("✅ `𝖲𝗎𝖼𝖼𝖾𝗌𝗌.`", buttons=get_back_button("gdrive"))

@callback("gdrive", owner=True)
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "☁️ 𝖢𝗅𝗂𝖼𝗄 **𝖠𝗎𝗍𝗁𝗈𝗋𝗂𝗌𝖾** 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗍𝗁𝖾 𝖼𝗈𝖽𝖾.\n\n𝖸𝗈𝗎 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗒𝗈𝗎𝗋 𝗈𝗐𝗇 𝖢𝖫𝖨𝖤𝖭𝖳 𝖨𝖣 𝖺𝗇𝖽 𝖲𝖤𝖢𝖱𝖤𝖳 𝖻𝗒 𝖼𝗁𝖾𝖼𝗄𝗂𝗇𝗀 [𝗍𝗁𝗂𝗌](https://t.me/UltroidUpdates/37).",
        buttons=[
            [Button.inline("📁 𝖥𝗈𝗅𝖽𝖾𝗋 𝖨𝖣", data="folderid"), Button.inline("🔐 𝖠𝗎𝗍𝗁𝗈𝗋𝗂𝗌𝖾", data="authorise")],
            [Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_otvars")],
        ],
        link_preview=False,
    )

@callback("dmof", owner=True)
async def rhwhe(e):
    if udB.get_key("DUAL_MODE"):
        udB.del_key("DUAL_MODE")
        key = "🔴 𝖮𝖿𝖿"
    else:
        udB.set_key("DUAL_MODE", "True")
        key = "🟢 𝖮𝗇"
    await e.edit(f"🌗 𝖣𝗎𝖺𝗅 𝖬𝗈𝖽𝖾: {key}", buttons=get_back_button("cbs_otvars"))

@callback("dmhn", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var, name = "DUAL_HNDLR", "Dual Handler"
    CH = udB.get_key(var) or "/"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(f"⚡ 𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝗌𝗒𝗆𝖻𝗈𝗅 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝖺𝗌 𝖧𝖺𝗇𝖽𝗅𝖾𝗋/𝖳𝗋𝗂𝗀𝗀𝖾𝗋 𝗍𝗈 𝗎𝗌𝖾 𝗒𝗈𝗎𝗋 𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍 𝖻𝗈𝗍.\n𝖸𝗈𝗎𝗋 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖧𝖺𝗇𝖽𝗅𝖾𝗋 𝗂𝗌 [ `{CH}` ]\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝖼𝖺𝗇𝖼𝖾𝗅.*")
        response = await conv.wait_event(events.NewMessage(chats=pru))
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message("🚫 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button("cbs_otvars"))
        elif len(themssg) > 1:
            await conv.send_message("❌ 𝖨𝗇𝖼𝗈𝗋𝗋𝖾𝖼𝗍 𝖧𝖺𝗇𝖽𝗅𝖾𝗋!", buttons=get_back_button("cbs_otvars"))
        else:
            await setit(event, var, themssg)
            await conv.send_message(f"✅ **{name}** 𝖼𝗁𝖺𝗇𝗀𝖾𝖽 𝗍𝗈 `{themssg}`", buttons=get_back_button("cbs_otvars"))

@callback("emoj", owner=True)
async def emoji(event):
    await event.delete()
    pru = event.sender_id
    var, name = "EMOJI_IN_HELP", f"Emoji in `{HNDLR}help` menu"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("😀 𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝖾𝗆𝗈𝗃𝗂 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗌𝖾𝗍.\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝖼𝖺𝗇𝖼𝖾𝗅.*")
        response = await conv.wait_event(events.NewMessage(chats=pru))
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message("🚫 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button("cbs_otvars"))
        elif themssg.startswith(("/", HNDLR)):
            await conv.send_message("❌ 𝖨𝗇𝖼𝗈𝗋𝗋𝖾𝖼𝗍 𝖤𝗆𝗈𝗃𝗂!", buttons=get_back_button("cbs_otvars"))
        else:
            await setit(event, var, themssg)
            await conv.send_message(f"✅ **{name}** 𝖼𝗁𝖺𝗇𝗀𝖾𝖽 𝗍𝗈 {themssg}", buttons=get_back_button("cbs_otvars"))

@callback("plg", owner=True)
async def pluginch(event):
    await event.delete()
    pru = event.sender_id
    var, name = "PLUGIN_CHANNEL", "Plugin Channel"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("🧩 𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝖨𝖣 𝗈𝗋 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾 𝗈𝖿 𝖺 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝖿𝗋𝗈𝗆 𝗐𝗁𝖾𝗋𝖾 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗂𝗇𝗌𝗍𝖺𝗅𝗅 𝖺𝗅𝗅 𝗉𝗅𝗎𝗀𝗂𝗇𝗌.\n\n*𝖮𝗎𝗋 𝖢𝗁𝖺𝗇𝗇𝖾𝗅:* @ultroidplugins\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝖼𝖺𝗇𝖼𝖾𝗅.*")
        response = await conv.wait_event(events.NewMessage(chats=pru))
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message("🚫 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button("cbs_otvars"))
        elif themssg.startswith(("/", HNDLR)):
            await conv.send_message("❌ 𝖨𝗇𝖼𝗈𝗋𝗋𝖾𝖼𝗍 𝖢𝗁𝖺𝗇𝗇𝖾𝗅!", buttons=get_back_button("cbs_otvars"))
        else:
            await setit(event, var, themssg)
            await conv.send_message(f"✅ **{name}** 𝖼𝗁𝖺𝗇𝗀𝖾𝖽 𝗍𝗈 `{themssg}`\n🔄 *𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗌𝗍𝖺𝗋𝗍 𝖺𝖿𝗍𝖾𝗋 𝗌𝖾𝗍𝗍𝗂𝗇𝗀.*", buttons=get_back_button("cbs_otvars"))

@callback("hhndlr", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var, name = "HNDLR", "Handler/Trigger"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(f"⚡ 𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝗌𝗒𝗆𝖻𝗈𝗅 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝖺𝗌 𝖧𝖺𝗇𝖽𝗅𝖾𝗋/𝖳𝗋𝗂𝗀𝗀𝖾𝗋 𝗍𝗈 𝗎𝗌𝖾 𝗍𝗁𝖾 𝖻𝗈𝗍.\n𝖸𝗈𝗎𝗋 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖧𝖺𝗇𝖽𝗅𝖾𝗋 𝗂𝗌 [ `{HNDLR}` ]\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝖼𝖺𝗇𝖼𝖾𝗅.*")
        response = await conv.wait_event(events.NewMessage(chats=pru))
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message("🚫 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button("cbs_otvars"))
        elif len(themssg) > 1:
            await conv.send_message("❌ 𝖨𝗇𝖼𝗈𝗋𝗋𝖾𝖼𝗍 𝖧𝖺𝗇𝖽𝗅𝖾𝗋!", buttons=get_back_button("cbs_otvars"))
        elif themssg.startswith(("/", "#", "@")):
            await conv.send_message("❌ 𝖳𝗁𝗂𝗌 𝖼𝖺𝗇𝗇𝗈𝗍 𝖻𝖾 𝗎𝗌𝖾𝖽 𝖺𝗌 𝖺 𝗁𝖺𝗇𝖽𝗅𝖾𝗋!", buttons=get_back_button("cbs_otvars"))
        else:
            await setit(event, var, themssg)
            await conv.send_message(f"✅ **{name}** 𝖼𝗁𝖺𝗇𝗀𝖾𝖽 𝗍𝗈 `{themssg}`", buttons=get_back_button("cbs_otvars"))

@callback("shndlr", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var, name = "SUDO_HNDLR", "Sudo Handler"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("👑 𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝗌𝗒𝗆𝖻𝗈𝗅 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝖺𝗌 𝖲𝗎𝖽𝗈 𝖧𝖺𝗇𝖽𝗅𝖾𝗋/𝖳𝗋𝗂𝗀𝗀𝖾𝗋 𝗍𝗈 𝗎𝗌𝖾 𝗍𝗁𝖾 𝖻𝗈𝗍.\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝖼𝖺𝗇𝖼𝖾𝗅.*")
        response = await conv.wait_event(events.NewMessage(chats=pru))
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message("🚫 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button("cbs_otvars"))
        elif len(themssg) > 1:
            await conv.send_message("❌ 𝖨𝗇𝖼𝗈𝗋𝗋𝖾𝖼𝗍 𝖧𝖺𝗇𝖽𝗅𝖾𝗋!", buttons=get_back_button("cbs_otvars"))
        elif themssg.startswith(("/", "#", "@")):
            await conv.send_message("❌ 𝖳𝗁𝗂𝗌 𝖼𝖺𝗇𝗇𝗈𝗍 𝖻𝖾 𝗎𝗌𝖾𝖽 𝖺𝗌 𝖺 𝗁𝖺𝗇𝖽𝗅𝖾𝗋!", buttons=get_back_button("cbs_otvars"))
        else:
            await setit(event, var, themssg)
            await conv.send_message(f"✅ **{name}** 𝖼𝗁𝖺𝗇𝗀𝖾𝖽 𝗍𝗈 `{themssg}`", buttons=get_back_button("cbs_otvars"))

@callback("taglog", owner=True)
async def tagloggrr(e):
    BUTTON = [
        [Button.inline("🟢 𝖲𝖤𝖳 𝖳𝖠𝖦 𝖫𝖮𝖦", data="abs_settag")],
        [Button.inline("🔴 𝖣𝖤𝖫𝖤𝖳𝖤 𝖳𝖠𝖦 𝖫𝖮𝖦", data="deltag")],
        get_back_button("cbs_otvars"),
    ]
    await e.edit("🏷️ **𝖢𝗁𝗈𝗈𝗌𝖾 𝖮𝗉𝗍𝗂𝗈𝗇𝗌:**", buttons=BUTTON)

@callback("deltag", owner=True)
async def _(e):
    udB.del_key("TAG_LOG")
    await e.answer("✅ 𝖣𝗈𝗇𝖾! 𝖳𝖺𝗀 𝖫𝗈𝗀𝗀𝖾𝗋 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗍𝗎𝗋𝗇𝖾𝖽 𝖮𝖿𝖿.")

@callback("eaddon", owner=True)
async def pmset(event):
    BT = [Button.inline("🔴 𝖠𝖽𝖽𝗈𝗇𝗌 𝖮𝖥𝖥", data="edof")] if udB.get_key("ADDONS") else [Button.inline("🟢 𝖠𝖽𝖽𝗈𝗇𝗌 𝖮𝖭", data="edon")]
    await event.edit("📦 **𝖠𝖣𝖣𝖮𝖭𝖲 ~ 𝖤𝗑𝗍𝗋𝖺 𝖯𝗅𝗎𝗀𝗂𝗇𝗌:**", buttons=[BT, [Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_otvars")]])

@callback("edon", owner=True)
async def eddon(event):
    await setit(event, "ADDONS", "True")
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖠𝖣𝖣𝖮𝖭𝖲 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗍𝗎𝗋𝗇𝖾𝖽 𝖮𝖭!\n🔄 *𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗌𝗍𝖺𝗋𝗍 𝖺𝖿𝗍𝖾𝗋 𝗌𝖾𝗍𝗍𝗂𝗇𝗀.*", buttons=get_back_button("eaddon"))

@callback("edof", owner=True)
async def eddof(event):
    udB.set_key("ADDONS", "False")
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖠𝖣𝖣𝖮𝖭𝖲 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗍𝗎𝗋𝗇𝖾𝖽 𝖮𝖥𝖥!\n🔄 *𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗌𝗍𝖺𝗋𝗍 𝖺𝖿𝗍𝖾𝗋 𝗌𝖾𝗍𝗍𝗂𝗇𝗀.*", buttons=get_back_button("eaddon"))

@callback("sudo", owner=True)
async def pmset(event):
    BT = [Button.inline("🔴 𝖲𝗎𝖽𝗈 𝖬𝗈𝖽𝖾 𝖮𝖥𝖥", data="ofsudo")] if udB.get_key("SUDO") else [Button.inline("🟢 𝖲𝗎𝖽𝗈 𝖬𝗈𝖽𝖾 𝖮𝖭", data="onsudo")]
    await event.edit(f"👑 **𝖲𝖴𝖣𝖮 𝖬𝖮𝖣𝖤** ~ 𝖲𝗈𝗆𝖾 𝗉𝖾𝗈𝗉𝗅𝖾 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗒𝗈𝗎𝗋 𝖻𝗈𝗍.\nℹ️ 𝖳𝗈 𝗄𝗇𝗈𝗐 𝗆𝗈𝗋𝖾, 𝗎𝗌𝖾 `{HNDLR}help sudo`.", buttons=[BT, [Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_otvars")]])

@callback("onsudo", owner=True)
async def eddon(event):
    await setit(event, "SUDO", "True")
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖲𝖴𝖣𝖮 𝖬𝖮𝖣𝖤 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗍𝗎𝗋𝗇𝖾𝖽 𝖮𝖭!\n🔄 *𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗌𝗍𝖺𝗋𝗍 𝖺𝖿𝗍𝖾𝗋 𝗌𝖾𝗍𝗍𝗂𝗇𝗀.*", buttons=get_back_button("sudo"))

@callback("ofsudo", owner=True)
async def eddof(event):
    await setit(event, "SUDO", "False")
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖲𝖴𝖣𝖮 𝖬𝖮𝖣𝖤 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗍𝗎𝗋𝗇𝖾𝖽 𝖮𝖥𝖥!\n🔄 *𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗌𝗍𝖺𝗋𝗍 𝖺𝖿𝗍𝖾𝗋 𝗌𝖾𝗍𝗍𝗂𝗇𝗀.*", buttons=get_back_button("sudo"))

@callback("sfgrp", owner=True)
async def sfgrp(event):
    await event.delete()
    var, name = "FBAN_GROUP_ID", "FBan Group ID"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(f"👥 𝖬𝖺𝗄𝖾 𝖺 𝗀𝗋𝗈𝗎𝗉, 𝖺𝖽𝖽 @MissRose_Bot, 𝗌𝖾𝗇𝖽 `{HNDLR}id`, 𝖼𝗈𝗉𝗒 𝗍𝗁𝖺𝗍 𝖺𝗇𝖽 𝗌𝖾𝗇𝖽 𝗂𝗍 𝗁𝖾𝗋𝖾.\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝗀𝗈 𝖻𝖺𝖼𝗄.*")
        response = await conv.wait_event(events.NewMessage(chats=pru))
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("🚫 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button("cbs_sfban"))
        await setit(event, var, themssg)
        await conv.send_message(f"✅ **{name}** 𝖼𝗁𝖺𝗇𝗀𝖾𝖽 𝗍𝗈 `{themssg}`", buttons=get_back_button("cbs_sfban"))

@callback("alvmed", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var, name = "ALIVE_PIC", "Alive Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("🖼️ **𝖠𝗅𝗂𝗏𝖾 𝖬𝖾𝖽𝗂𝖺**\n𝖲𝖾𝗇𝖽 𝗆𝖾 𝖺 𝗉𝗂𝖼/𝗀𝗂𝖿/𝗆𝖾𝖽𝗂𝖺 𝗍𝗈 𝗌𝖾𝗍 𝖺𝗌 𝖺𝗅𝗂𝗏𝖾 𝗆𝖾𝖽𝗂𝖺.\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝗍𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾.*")
        response = await conv.get_response()
        try:
            if response.message == "/cancel":
                return await conv.send_message("🚫 𝖮𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button("cbs_alvcstm"))
        except BaseException as er:
            LOGS.exception(er)
        if not response.text.startswith("/") and response.text != "" and (not response.media or isinstance(response.media, MessageMediaWebPage)):
            url = text_to_url(response)
        elif response.sticker:
            url = response.file.id
        else:
            media = await event.client.download_media(response, "alvpc")
            try:
                url = uploader.upload_file(media)
                remove(media)
            except BaseException as er:
                LOGS.exception(er)
                return await conv.send_message("❌ 𝖳𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾𝖽.", buttons=get_back_button("cbs_alvcstm"))
        await setit(event, var, url)
        await conv.send_message(f"✅ **{name}** 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝖾𝗍.", buttons=get_back_button("cbs_alvcstm"))

@callback("delmed", owner=True)
async def dell(event):
    try:
        udB.del_key("ALIVE_PIC")
        return await event.edit(get_string("clst_5"), buttons=get_back_button("cbs_alabs_vcstm"))
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(get_string("clst_4"), buttons=get_back_button("cbs_alabs_vcstm"))

@callback("inpm_in", owner=True)
async def inl_on(event):
    await setit(event, "INLINE_PM", "True")
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝗍𝗒𝗉𝖾 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝖾𝗍 𝗍𝗈 **𝖨𝗇𝗅𝗂𝗇𝖾**!", buttons=[[Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_pmtype")]])

@callback("inpm_no", owner=True)
async def inl_on(event):
    await setit(event, "INLINE_PM", "False")
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝗍𝗒𝗉𝖾 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝖾𝗍 𝗍𝗈 **𝖭𝗈𝗋𝗆𝖺𝗅**!", buttons=[[Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_pmtype")]])

@callback("pmtxt", owner=True)
async def name(event):
    await event.delete()
    pru = event.sender_id
    var, name = "PM_TEXT", "PM Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("📝 **𝖯𝖬 𝖳𝖾𝗑𝗍**\n𝖤𝗇𝗍𝖾𝗋 𝗍𝗁𝖾 𝗇𝖾𝗐 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝗍𝖾𝗑𝗍.\n\n💡 *𝖸𝗈𝗎 𝖼𝖺𝗇 𝗎𝗌𝖾* `{name}`, `{fullname}`, `{count}`, `{mention}`, `{username}` *𝖺𝗌 𝗉𝗅𝖺𝖼𝖾𝗁𝗈𝗅𝖽𝖾𝗋𝗌.*\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝗍𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾.*")
        response = await conv.wait_event(events.NewMessage(chats=pru))
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("🚫 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button("cbs_pmcstm"))
        if len(themssg) > 4090:
            return await conv.send_message("❌ 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝗍𝗈𝗈 𝗅𝗈𝗇𝗀! 𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗌𝗁𝗈𝗋𝗍𝖾𝗋 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.", buttons=get_back_button("cbs_pmcstm"))
        await setit(event, var, themssg)
        await conv.send_message(f"✅ **{name}** 𝖼𝗁𝖺𝗇𝗀𝖾𝖽 𝗍𝗈:\n`{themssg}`\n\n🔄 *𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗌𝗍𝖺𝗋𝗍 𝖺𝖿𝗍𝖾𝗋 𝗌𝖾𝗍𝗍𝗂𝗇𝗀.*", buttons=get_back_button("cbs_pmcstm"))

@callback("swarn", owner=True)
async def name(event):
    tultd = [Button.inline(f"{x}", data=f"wrns_{x}") for x in range(1, 10)]
    lst = list(zip(tultd[::3], tultd[1::3], tultd[2::3]))
    lst.append([Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_pmcstm")])
    await event.edit("⚠️ 𝖲𝖾𝗅𝖾𝖼𝗍 𝗍𝗁𝖾 𝗇𝗎𝗆𝖻𝖾𝗋 𝗈𝖿 𝗐𝖺𝗋𝗇𝗂𝗇𝗀𝗌 𝖿𝗈𝗋 𝖺 𝗎𝗌𝖾𝗋 𝖻𝖾𝖿𝗈𝗋𝖾 𝗀𝖾𝗍𝗍𝗂𝗇𝗀 𝖻𝗅𝗈𝖼𝗄𝖾𝖽 𝗂𝗇 𝖯𝖬𝗌.", buttons=lst)

@callback(re.compile(b"wrns_(.*)"), owner=True)
async def set_wrns(event):
    value = int(event.data_match.group(1).decode("UTF-8"))
    if udB.set_key("PMWARNS", value):
        await event.edit(f"✅ 𝖯𝖬 𝖶𝖺𝗋𝗇𝗌 𝗌𝖾𝗍 𝗍𝗈 **{value}**.\n𝖭𝖾𝗐 𝗎𝗌𝖾𝗋𝗌 𝗐𝗂𝗅𝗅 𝗁𝖺𝗏𝖾 {value} 𝖼𝗁𝖺𝗇𝖼𝖾𝗌 𝗂𝗇 𝖯𝖬𝗌 𝖻𝖾𝖿𝗈𝗋𝖾 𝗀𝖾𝗍𝗍𝗂𝗇𝗀 𝖻𝖺𝗇𝗇𝖾𝖽.", buttons=get_back_button("cbs_pmcstm"))
    else:
        await event.edit(f"❌ 𝖲𝗈𝗆𝖾𝗍𝗁𝗂𝗇𝗀 𝗐𝖾𝗇𝗍 𝗐𝗋𝗈𝗇𝗀, 𝗉𝗅𝖾𝖺𝗌𝖾 𝖼𝗁𝖾𝖼𝗄 𝗒𝗈𝗎𝗋 `{HNDLR}logs`!", buttons=get_back_button("cbs_pmcstm"))

@callback("pmmed", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var, name = "PMPIC", "PM Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("🖼️ **𝖯𝖬 𝖬𝖾𝖽𝗂𝖺**\n𝖲𝖾𝗇𝖽 𝗆𝖾 𝖺 𝗉𝗂𝖼/𝗀𝗂𝖿/𝗌𝗍𝗂𝖼𝗄𝖾𝗋/𝗅𝗂𝗇𝗄 𝗍𝗈 𝗌𝖾𝗍 𝖺𝗌 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝗆𝖾𝖽𝗂𝖺.\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝗍𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾.*")
        response = await conv.get_response()
        try:
            if response.message == "/cancel":
                return await conv.send_message("🚫 𝖮𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button("cbs_pmcstm"))
        except BaseException as er:
            LOGS.exception(er)
        media = await event.client.download_media(response, "pmpc")
        if not response.text.startswith("/") and response.text != "" and (not response.media or isinstance(response.media, MessageMediaWebPage)):
            url = text_to_url(response)
        elif response.sticker:
            url = response.file.id
        else:
            try:
                url = uploader.upload_file(media)
                remove(media)
            except BaseException as er:
                LOGS.exception(er)
                return await conv.send_message("❌ 𝖳𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾𝖽.", buttons=get_back_button("cbs_pmcstm"))
        await setit(event, var, url)
        await conv.send_message(f"✅ **{name}** 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝖾𝗍.", buttons=get_back_button("cbs_pmcstm"))

@callback("delpmmed", owner=True)
async def dell(event):
    try:
        udB.del_key("PMPIC")
        return await event.edit(get_string("clst_5"), buttons=get_back_button("cbs_pmcstm"))
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(get_string("clst_4"), buttons=[[Button.inline("« 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌", data="setter")]])

@callback("apon", owner=True)
async def apon(event):
    await setit(event, "AUTOAPPROVE", "True")
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖠𝖴𝖳𝖮𝖠𝖯𝖯𝖱𝖮𝖵𝖤 𝖲𝗍𝖺𝗋𝗍𝖾𝖽!", buttons=[[Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_apauto")]])

@callback("apof", owner=True)
async def apof(event):
    try:
        udB.set_key("AUTOAPPROVE", "False")
        return await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖠𝖴𝖳𝖮𝖠𝖯𝖯𝖱𝖮𝖵𝖤 𝖲𝗍𝗈𝗉𝗉𝖾𝖽!", buttons=[[Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_apauto")]])
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(get_string("clst_4"), buttons=[[Button.inline("« 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌", data="setter")]])

@callback("pml", owner=True)
async def l_vcs(event):
    BT = [Button.inline("🔴 𝖯𝖬𝖫𝖮𝖦𝖦𝖤𝖱 𝖮𝖥𝖥", data="pmlogof")] if udB.get_key("PMLOG") else [Button.inline("🟢 𝖯𝖬𝖫𝖮𝖦𝖦𝖤𝖱 𝖮𝖭", data="pmlog")]
    await event.edit("🗂️ **𝖯𝖬𝖫𝖮𝖦𝖦𝖤𝖱** ~ 𝖳𝗁𝗂𝗌 𝗐𝗂𝗅𝗅 𝖿𝗈𝗋𝗐𝖺𝗋𝖽 𝗒𝗈𝗎𝗋 𝖯𝖬𝗌 𝗍𝗈 𝗒𝗈𝗎𝗋 𝖯𝗋𝗂𝗏𝖺𝗍𝖾 𝖦𝗋𝗈𝗎𝗉:", buttons=[BT, [Button.inline("🗂️ 𝖯𝗆𝖫𝗈𝗀𝗀𝖾𝗋 𝖦𝗋𝗈𝗎𝗉", "abs_pmlgg")], [Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_pmcstm")]])

@callback("pmlog", owner=True)
async def pmlog(event):
    await setit(event, "PMLOG", "True")
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖯𝖬𝖫𝖮𝖦𝖦𝖤𝖱 𝖲𝗍𝖺𝗋𝗍𝖾𝖽!", buttons=[[Button.inline("« 𝖡𝖺𝖼𝗄", data="pml")]])

@callback("pmlogof", owner=True)
async def pmlogof(event):
    try:
        udB.del_key("PMLOG")
        return await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖯𝖬𝖫𝖮𝖦𝖦𝖤𝖱 𝖲𝗍𝗈𝗉𝗉𝖾𝖽!", buttons=[[Button.inline("« 𝖡𝖺𝖼𝗄", data="pml")]])
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(get_string("clst_4"), buttons=[[Button.inline("« 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌", data="setter")]])

@callback("pmon", owner=True)
async def pmonn(event):
    await setit(event, "PMSETTING", "True")
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗍𝗎𝗋𝗇𝖾𝖽 𝖮𝖭!", buttons=[[Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_ppmset")]])

@callback("pmoff", owner=True)
async def pmofff(event):
    await setit(event, "PMSETTING", "False")
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖯𝖬𝖯𝖾𝗋𝗆𝗂𝗍 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗍𝗎𝗋𝗇𝖾𝖽 𝖮𝖥𝖥!", buttons=[[Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_ppmset")]])

@callback("botmew", owner=True)
async def hhh(e):
    async with e.client.conversation(e.chat_id) as conv:
        await conv.send_message("🖼️ 𝖲𝖾𝗇𝖽 𝖺𝗇𝗒 𝗆𝖾𝖽𝗂𝖺 𝗍𝗈 𝗄𝖾𝖾𝗉 𝖺𝗍 𝗒𝗈𝗎𝗋 𝖡𝗈𝗍'𝗌 𝗐𝖾𝗅𝖼𝗈𝗆𝖾.")
        msg = await conv.get_response()
        if not msg.media or msg.text.startswith("/"):
            return await conv.send_message("❌ 𝖳𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾𝖽!", buttons=get_back_button("cbs_chatbot"))
        udB.set_key("STARTMEDIA", msg.file.id)
        await conv.send_message("✅ 𝖣𝗈𝗇𝖾!", buttons=get_back_button("cbs_chatbot"))

@callback("botinfe", owner=True)
async def hhh(e):
    async with e.client.conversation(e.chat_id) as conv:
        await conv.send_message("ℹ️ 𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗍𝗈 𝖽𝗂𝗌𝗉𝗅𝖺𝗒 𝗐𝗁𝖾𝗇 𝖺 𝗎𝗌𝖾𝗋 𝗉𝗋𝖾𝗌𝗌𝖾𝗌 𝗍𝗁𝖾 𝖨𝗇𝖿𝗈 𝖻𝗎𝗍𝗍𝗈𝗇 𝗂𝗇 𝖡𝗈𝗍 𝖶𝖾𝗅𝖼𝗈𝗆𝖾!\n\n*𝖲𝖾𝗇𝖽 `False` 𝗍𝗈 𝖼𝗈𝗆𝗉𝗅𝖾𝗍𝖾𝗅𝗒 𝗋𝖾𝗆𝗈𝗏𝖾 𝗍𝗁𝖺𝗍 𝖻𝗎𝗍𝗍𝗈𝗇.*")
        msg = await conv.get_response()
        if msg.media or msg.text.startswith("/"):
            return await conv.send_message("❌ 𝖳𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾𝖽!", buttons=get_back_button("cbs_chatbot"))
        udB.set_key("BOT_INFO_START", msg.text)
        await conv.send_message("✅ 𝖣𝗈𝗇𝖾!", buttons=get_back_button("cbs_chatbot"))

@callback("pmfs", owner=True)
async def heheh(event):
    Ll, err = [], ""
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message("📢 𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝖢𝗁𝖺𝗍 𝖨𝖣(𝗌) 𝗐𝗁𝗂𝖼𝗁 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗎𝗌𝖾𝗋𝗌 𝗍𝗈 𝗃𝗈𝗂𝗇 𝖻𝖾𝖿𝗈𝗋𝖾 𝗎𝗌𝗂𝗇𝗀 𝖢𝗁𝖺𝗍/𝖯𝗆 𝖡𝗈𝗍.\n\n*𝖲𝖾𝗇𝖽 /clear 𝗍𝗈 𝖽𝗂𝗌𝖺𝖻𝗅𝖾 𝖯𝗆𝖡𝗈𝗍 𝖥𝗈𝗋𝖼𝖾𝖲𝗎𝖻.*\n*𝖲𝖾𝗇𝖽 /cancel 𝗍𝗈 𝗌𝗍𝗈𝗉 𝗍𝗁𝗂𝗌 𝗉𝗋𝗈𝖼𝖾𝗌𝗌.*\n\n💡 **𝖤𝗑𝖺𝗆𝗉𝗅𝖾:**\n`-1001234567\n-100778888`")
        try:
            msg = await conv.get_response()
        except AsyncTimeOut:
            return await conv.send_message("⏳ **𝖳𝗂𝗆𝖾 𝖴𝗉!**\n𝖲𝗍𝖺𝗋𝗍 𝖿𝗋𝗈𝗆 `/start` 𝖺𝗀𝖺𝗂𝗇.")
        if not msg.text or msg.text.startswith("/"):
            timyork = "🚫 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!"
            if msg.text == "/clear":
                udB.del_key("PMBOT_FSUB")
                timyork = "✅ 𝖣𝗈𝗇𝖾! 𝖥𝗈𝗋𝖼𝖾 𝖲𝗎𝖻𝗌𝖼𝗋𝗂𝖻𝖾 𝖲𝗍𝗈𝗉𝗉𝖾𝖽.\n🔄 *𝖱𝖾𝗌𝗍𝖺𝗋𝗍 𝗒𝗈𝗎𝗋 𝖡𝗈𝗍!*"
            return await conv.send_message(timyork, buttons=get_back_button("cbs_chatbot"))
        for chat in msg.message.split("\n"):
            chat = int(chat) if chat.startswith("-") or chat.isdigit() else chat
            try:
                CHSJSHS = await event.client.get_entity(chat)
                Ll.append(get_peer_id(CHSJSHS))
            except Exception as er:
                err += f"❌ **{chat}** : `{er}`\n"
        if err:
            return await conv.send_message(err)
        udB.set_key("PMBOT_FSUB", str(Ll))
        await conv.send_message("✅ 𝖣𝗈𝗇𝖾!\n🔄 *𝖱𝖾𝗌𝗍𝖺𝗋𝗍 𝗒𝗈𝗎𝗋 𝖡𝗈𝗍.*", buttons=get_back_button("cbs_chatbot"))

@callback("bwel", owner=True)
async def name(event):
    await event.delete()
    pru = event.sender_id
    var, name = "STARTMSG", "Bot Welcome Message"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("👋 **𝖡𝖮𝖳 𝖶𝖤𝖫𝖢𝖮𝖬𝖤 𝖬𝖲𝖦**\n𝖤𝗇𝗍𝖾𝗋 𝗍𝗁𝖾 𝗆𝗌𝗀 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗌𝗁𝗈𝗐 𝗐𝗁𝖾𝗇 𝗌𝗈𝗆𝖾𝗈𝗇𝖾 𝗌𝗍𝖺𝗋𝗍𝗌 𝗒𝗈𝗎𝗋 𝖠𝗌𝗌𝗂𝗌𝗍𝖺𝗇𝗍 𝖡𝗈𝗍.\n💡 *𝖸𝗈𝗎 𝖼𝖺𝗇 𝗎𝗌𝖾* `{me}`, `{mention}` *𝗉𝖺𝗋𝖺𝗆𝖾𝗍𝖾𝗋𝗌 𝗍𝗈𝗈.*\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝗍𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾.*")
        response = await conv.wait_event(events.NewMessage(chats=pru))
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message("🚫 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button("cbs_chatbot"))
        await setit(event, var, themssg)
        await conv.send_message(f"✅ **{name}** 𝖼𝗁𝖺𝗇𝗀𝖾𝖽 𝗍𝗈:\n`{themssg}`", buttons=get_back_button("cbs_chatbot"))

@callback("onchbot", owner=True)
async def chon(event):
    await setit(event, "PMBOT", "True")
    Loader(path="assistant/pmbot.py", key="PM Bot").load()
    if AST_PLUGINS.get("pmbot"):
        for i, e in AST_PLUGINS["pmbot"]:
            event.client.remove_event_handler(i)
            event.client.add_event_handler(i, events.NewMessage(**e))
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖭𝗈𝗐 𝗒𝗈𝗎 𝖼𝖺𝗇 𝖼𝗁𝖺𝗍 𝗐𝗂𝗍𝗁 𝗉𝖾𝗈𝗉𝗅𝖾 𝗏𝗂𝖺 𝗍𝗁𝗂𝗌 𝖻𝗈𝗍.", buttons=[Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_chatbot")])

@callback("ofchbot", owner=True)
async def chon(event):
    await setit(event, "PMBOT", "False")
    if AST_PLUGINS.get("pmbot"):
        for i, e in AST_PLUGINS["pmbot"]:
            event.client.remove_event_handler(i)
    await event.edit("✅ 𝖣𝗈𝗇𝖾! 𝖢𝗁𝖺𝗍𝗍𝗂𝗇𝗀 𝗏𝗂𝖺 𝗍𝗁𝗂𝗌 𝖻𝗈𝗍 𝗌𝗍𝗈𝗉𝗉𝖾𝖽.", buttons=[Button.inline("« 𝖡𝖺𝖼𝗄", data="cbs_chatbot")])

@callback("inli_pic", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var, name = "INLINE_PIC", "Inline Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("🖼️ **𝖨𝗇𝗅𝗂𝗇𝖾 𝖬𝖾𝖽𝗂𝖺**\n𝖲𝖾𝗇𝖽 𝗆𝖾 𝖺 𝗉𝗂𝖼/𝗀𝗂𝖿 𝗈𝗋 𝗅𝗂𝗇𝗄 𝗍𝗈 𝗌𝖾𝗍 𝖺𝗌 𝗂𝗇𝗅𝗂𝗇𝖾 𝗆𝖾𝖽𝗂𝖺.\n\n*𝖴𝗌𝖾 /cancel 𝗍𝗈 𝗍𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾.*")
        response = await conv.get_response()
        try:
            if response.message == "/cancel":
                return await conv.send_message("🚫 𝖮𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽!", buttons=get_back_button("setter"))
        except BaseException as er:
            LOGS.exception(er)
        media = await event.client.download_media(response, "inlpic")
        if not response.text.startswith("/") and response.text != "" and (not response.media or isinstance(response.media, MessageMediaWebPage)):
            url = text_to_url(response)
        else:
            try:
                url = uploader.upload_file(media)
                remove(media)
            except BaseException as er:
                LOGS.exception(er)
                return await conv.send_message("❌ 𝖳𝖾𝗋𝗆𝗂𝗇𝖺𝗍𝖾𝖽.", buttons=get_back_button("setter"))
        await setit(event, var, url)
        await conv.send_message(f"✅ **{name}** 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝖾𝗍.", buttons=get_back_button("setter"))

FD_MEDIA = {}

@callback(re.compile("fd(.*)"), owner=True)
async def fdroid_dler(event):
    uri = event.data_match.group(1).decode("utf-8")
    if cached_media := FD_MEDIA.get(uri):
        return await event.edit(file=cached_media)
    await event.answer("⬇️ 𝖲𝗍𝖺𝗋𝗍𝗂𝗇𝗀 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽...", alert=True)
    await event.edit("⏳ 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝗂𝗇𝗀...")
    URL = f"https://f-droid.org/packages/{uri}"
    conte = await async_searcher(URL, re_content=True)
    BSC = bs(conte, "html.parser", from_encoding="utf-8")
    dl_ = BSC.find("p", "package-version-download").find("a")["href"]
    title = BSC.find("h3", "package-name").text.strip()
    thumb = BSC.find("img", "package-icon")["src"]
    thumb = f"https://f-droid.org{thumb}" if thumb.startswith("/") else thumb
    thumb, _ = await fast_download(thumb, filename=f"{uri}.png")
    s_time = time.time()
    file, _ = await fast_download(
        dl_,
        filename=f"{title}.apk",
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, event, s_time, "🚀 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝗂𝗇𝗀...")
        ),
    )
    n_file = await event.client.fast_uploader(file, show_progress=True, event=event, message="📤 𝖴𝗉𝗅𝗈𝖺𝖽𝗂𝗇𝗀...", to_delete=True)
    buttons = Button.switch_inline("🔍 𝖲𝖾𝖺𝗋𝖼𝗁 𝖡𝖺𝖼𝗄", query="fdroid", same_peer=True)
    try:
        msg = await event.edit(f"**📦 [{title}]({URL})**", file=n_file, thumb=thumb, buttons=buttons)
    except Exception as er:
        LOGS.exception(er)
        try:
            msg = await event.client.edit_message(await event.get_input_chat(), event.message_id, f"**📦 [{title}]({URL})**", buttons=buttons, thumb=thumb, file=n_file)
        except Exception as er:
            remove(thumb)
            LOGS.exception(er)
            return await event.edit(f"**❌ 𝖤𝖱𝖱𝖮𝖱**: `{er}`", buttons=buttons)
    if msg and hasattr(msg, "media"):
        FD_MEDIA[uri] = msg.media
    remove(thumb)
