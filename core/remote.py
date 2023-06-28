import os, json
import time, sys
import subprocess
from .config import Var
from contextlib import suppress
from logging import getLogger
from contextlib import contextmanager
from utilities.helper import fetch_sync, run_async, fetch
from importlib import import_module

LOCK_PATH = "./ultroid-lock.json"
Logger = getLogger("Remote")


class Remote:
    REMOTE_URL = Var.REMOTE_URI or "https://plugins.xditya.me"
    MAX_HR = 1
    DEF_CONFIG = {"plugins": {}, "helpers": {}, "manager": {}}

    def __init__(self) -> None:
        self._modules = {}
        self._deps = []
        self._status_fetch = None

        if os.path.exists(LOCK_PATH):
            with open(LOCK_PATH, "r") as file:
                try:
                    self.RemoteConfig: dict = json.load(file)
                except json.decoder.JSONDecodeError:
                    Logger.error("Failed to decode ultroid lock file, creating new...")
                    self.RemoteConfig = self.DEF_CONFIG
        else:
            self.RemoteConfig = self.DEF_CONFIG

    def _http_import(self, path: str, save_as=None, helper=False, manager=False):
        if not save_as:
            save_as = f"{path}.py"
        if helper:
            _pat = "helpers"
            mid = "helper"
        elif manager:
            _pat = mid = "manager"
        else:
            _pat, mid = "plugins", ""
        in_local = self.RemoteConfig[_pat].get(path)
        _exists = os.path.exists(save_as)

        # Last fetched in less than avoided time gap.
        if in_local and self.get_status() and _exists:
            return save_as
        details: dict = fetch_sync(f"{self.REMOTE_URL}/search{mid}/{path}", True)  # type: ignore
        if details.get("status") == 404:
            Logger.debug(f"got 404 response, {details}")
            return
        if in_local and in_local["version"] == details.get("version") and _exists:
            return save_as
        if details.get("deps"):
            self.__install_deps(details["deps"])
        remote_file = fetch_sync(
            f"{self.REMOTE_URL}/get{mid}/{path}",
            evaluate=lambda e: e.content if e.status_code == 200 else None,
        )

        if remote_file:
            with open(save_as, "wb") as file:
                file.write(remote_file)  # type: ignore

            with suppress(KeyError):
                del details["repo"]
            del details["path"]

            self.RemoteConfig[_pat][path] = details
            return save_as

    @contextmanager
    def get(self, path_: str, save_as=None, force: bool = False, *args, **kwargs):
        _save = kwargs.get("_save", True)
        _load = kwargs.get("_load", True)
        _dispose = kwargs.get("dispose", False)
        for key in ["_save", "dispose", "_load"]:
            with suppress(KeyError):
                del kwargs[key]
        if not force:
            with suppress(KeyError):
                yield self._modules[path_]
                return
        try:
            if _load and (path := self._http_import(path_, save_as, *args, **kwargs)):
                path = path[:-3].replace("/", ".").replace("\\", ".")
                modl = import_module(path)
                self._modules[path_] = modl
                yield modl
        finally:
            if _dispose:
                os.remove(
                    save_as if (save_as and os.path.exists(save_as)) else f"{path_}.py"
                )
            if _save:
                self.save()

    async_get = run_async(get)
    _async_import = run_async(_http_import)

    async def async_import(self, *args, **kwargs):
        try:
            return await self._async_import(*args, **kwargs)
        except Exception as er:
            Logger.exception(er)

    def __install_deps(self, deps: list):
        # TODO: Improve
        proc = []
        for dep in deps:
            depc = None
            if isinstance(dep, list):
                depc, dep = dep
            if dep in self._deps:
                continue
            if not depc:
                depc = dep.split("[")[0].split("=")[0]
            try:
                import_module(depc)
            except ModuleNotFoundError:
                print(f"Installing {dep}", end="\r")
                proc.append(
                    subprocess.Popen(
                        [sys.executable, "-m", "pip", "install", dep],
                        stderr=subprocess.PIPE,
                    )
                )
            self._deps.append(dep)
        for prc in proc:
            prc.wait(timeout=10000)
            if err:= prc.stderr.read():
                Logger.error(err)

    async def get_all_plugins(self, end):
        return await fetch(f"{self.REMOTE_URL}/{end}", re_json=True)

    def get_info(self, id):
        return self.RemoteConfig["plugins"].get(id, {})

    def get_status(self):
        if self._status_fetch:
            return True
        if tim := self.RemoteConfig.get("last_fetched"):
            if ((time.time() - tim) / (1000 * 60 * 60)) < self.MAX_HR:
                self._status_fetch = True
                return True

    def set_status_done(self):
        if self.get_status():
            return
        self.RemoteConfig["last_fetched"] = time.time()
        self.save()

    def fetch_lang(
        self, langCode, strings_path="localization/strings", defaultLang="en"
    ):
        filePath = f"{strings_path}/{langCode}.yml"
        if self.get_status() and os.path.exists(filePath):
            return

        def evaluate(req):
            if req.headers["content-type"] == "application/json":
                Logger.error(f"Invalid Response recieved, {req.json()}")

                if langCode != defaultLang and not os.path.exists(
                   filePath
                ):
                    return self.fetch_lang(defaultLang)
                return

            with open(filePath, "wb") as file:
                file.write(req.content)

            return filePath

        return fetch_sync(
            f"{self.REMOTE_URL}/getlanguage/{langCode}", evaluate=evaluate
        )
    
    async def getLanguages(self):
        return await fetch(f"{self.REMOTE_URL}/getlanguage", re_json=True)

    def save(self):
        with open(LOCK_PATH, "w") as file:
            json.dump(self.RemoteConfig, file)


rm = Remote()
