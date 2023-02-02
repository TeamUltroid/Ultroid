import os

from core.config import LOGS
from core.loader import load
from utilities.helper import bash

VCBOT_REPO = "https://github.com/TeamUltroid/VCbot"


async def setup():
    try:
        pass
    except ModuleNotFoundError as er:
        LOGS.error(f"'{er.name}' is not Installed! Skipping loading of VCBOT.")
        return
    if not os.path.exists("resources/downloads"):
        os.mkdir("resources/downloads")
    if not os.path.exists("modules/vcbot"):
        await bash(f"git clone {VCBOT_REPO} modules/vcbot")
    else:
        await bash("cd modules/vcbot && git pull")
    try:
        load(path="modules/vcbot", key="VCBot")
    except Exception as er:
        LOGS.exception(er)
