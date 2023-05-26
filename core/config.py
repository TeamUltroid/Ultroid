# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import os
from decouple import config
from ast import literal_eval

class Config:
    def __getattr__(self, __name: str):
        if __name in self.__dict__:
            return self.__dict__[__name]
        _data = config(__name, default="")
        try:
            return literal_eval(_data)
        except Exception:
            return _data

    API_ID = config("API_ID", cast=int, default=6)
    API_HASH = config("API_HASH", default="eb06d4abfb49dc3eeb1aeb98ae0f581e")


def detect_platform():
    if os.getenv("DYNO"):
        return "heroku"
    if os.getenv("RAILWAY_STATIC_URL"):
        return "railway"
    if os.getenv("RENDER_SERVICE_NAME"):
        return "render"
    if os.getenv("OKTETO_TOKEN"):
        return "okteto"
    if os.getenv("KUBERNETES_PORT"):
        return "qovery | kubernetes"
    if os.getenv("RUNNER_USER") or os.getenv("HOSTNAME"):
        return "codespace" if os.getenv("USER") == "codespace" else "github actions"
    if os.getenv("ANDROID_ROOT"):
        return "termux"
    return "fly.io" if os.getenv("FLY_APP_NAME") else "local"


HOSTED_ON = detect_platform()
Var = Config()