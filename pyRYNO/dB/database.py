# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from decouple import config
from dotenv import load_dotenv, find_dotenv
from . import *


load_dotenv(find_dotenv())


class Var(object):
    # Mandatory
    API_ID = config("API_ID", default=None, cast=int)
    API_HASH = config("API_HASH", default=None)
    BOT_TOKEN = config("BOT_TOKEN", default=None)
    BOT_USERNAME = config("BOT_USERNAME", default=None)
    SESSION = config("SESSION", default=None)
    DB_URI = config("DATABASE_URL", default=None)
    LOG_CHANNEL = config("LOG_CHANNEL", default=None, cast=int)
    BLACKLIST_CHAT = set(int(x) for x in config("BLACKLIST_CHAT", "").split())
    # bot mode
    BOT_MODE = config("BOT_MODE", default=False, cast=bool)
    try:
        OWNER_ID = config("OWNER_ID", default=None, cast=int)
    except BaseException:
        pass
    # heroku stuff
    try:
        HEROKU_APP_NAME = config("HEROKU_APP_NAME", default=None)
        HEROKU_API = config("HEROKU_API", default=None)
    except BaseException:
        HEROKU_APP_NAME = None
        HEROKU_API = None
    # REDIS
    REDIS_URI = config("REDIS_URI", default=None)
    REDIS_PASSWORD = config("REDIS_PASSWORD", default=None)
