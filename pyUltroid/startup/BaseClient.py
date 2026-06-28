# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import asyncio
import contextlib
import mimetypes
import os
import sys
import time
from logging import Logger
from pathlib import Path

# Ultroid relies on a forked Telethon ("telethonpatch") for a few extra
# behaviours. Keep importing the patched client.
from telethonpatch import TelegramClient
from telethon import utils as telethon_utils
from telethon.errors import (
    AccessTokenExpiredError,
    AccessTokenInvalidError,
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
)
from telethon.tl.types import DocumentAttributeFilename

from ..configs import Var
from . import *  # noqa: F401,F403 - exposes LOGS / TelethonLogger


class UltroidClient(TelegramClient):
    """Ultroid-flavoured ``TelegramClient`` with extra conveniences.

    The previous implementation had two long-standing footguns:

    * a ``__dict__`` ``@property`` that returned ``self.me.to_dict()`` and
      therefore broke normal instance attribute lookup; and
    * a ``while not raw_file:`` busy-loop in ``fast_uploader`` /
      ``fast_downloader`` that could spin forever if the underlying
      ``upload_file`` / ``download_file`` ever returned a falsy value.

    Both have been fixed below. All other public APIs are unchanged.
    """

    def __init__(
        self,
        session,
        api_id=None,
        api_hash=None,
        bot_token=None,
        udB=None,
        logger: Logger = LOGS,  # noqa: F405
        log_attempt: bool = True,
        exit_on_error: bool = True,
        *args,
        **kwargs,
    ):
        self._cache = {}
        self._dialogs = []
        self._handle_error = exit_on_error
        self._log_at = log_attempt
        self.logger = logger
        self.udB = udB
        kwargs["api_id"] = api_id or Var.API_ID
        kwargs["api_hash"] = api_hash or Var.API_HASH
        kwargs["base_logger"] = TelethonLogger  # noqa: F405
        super().__init__(session, **kwargs)
        self.run_in_loop(self.start_client(bot_token=bot_token))
        self.dc_id = self.session.dc_id

    def __repr__(self) -> str:
        return f"<UltroidClient self={self.full_name!r} bot={self._bot}>"

    # ---------------------------------------------------------- login
    async def start_client(self, **kwargs) -> None:
        """Connect & cache identity information."""
        if self._log_at:
            self.logger.info("Logging in to Telegram...")
        try:
            await self.start(**kwargs)
        except ApiIdInvalidError:
            self.logger.critical("API_ID / API_HASH combination is invalid.")
            sys.exit(1)
        except (AuthKeyDuplicatedError, EOFError):
            self.logger.critical("String session expired. Create a new one!")
            if self._handle_error:
                sys.exit(1)
            return
        except (AccessTokenExpiredError, AccessTokenInvalidError):
            # AccessTokenError can only occur for Bot accounts and the token
            # was already persisted in the DB during startup.
            if self.udB is not None:
                self.udB.del_key("BOT_TOKEN")
            self.logger.critical(
                "BOT_TOKEN is expired or invalid. Create a new one via @BotFather "
                "and update the BOT_TOKEN env variable."
            )
            sys.exit(1)

        self.me = await self.get_me()
        if self.me.bot:
            who = f"@{self.me.username}"
        else:
            # Userbots should never log/store their phone number.
            self.me.phone = None
            who = self.full_name
        if self._log_at:
            self.logger.info(f"Logged in as {who}.")
        self._bot = await self.is_bot()

    # ------------------------------------------------------ fast IO
    async def fast_uploader(self, file, **kwargs):
        """Upload ``file`` using parallel MTProto senders.

        Supported kwargs (all optional):

        * ``filename`` – override the uploaded filename
        * ``show_progress`` + ``event`` – display a progress bar
        * ``use_cache`` – reuse previously uploaded ``InputFile`` (default True)
        * ``to_delete`` – remove the local file after a successful upload
        * ``message`` – progress-bar caption
        """
        start_time = time.time()
        path = Path(file)
        filename = kwargs.get("filename", path.name)
        show_progress = kwargs.get("show_progress", False)
        event = kwargs.get("event") if show_progress else None
        use_cache = kwargs.get("use_cache", True)
        to_delete = kwargs.get("to_delete", False)
        message = kwargs.get("message", f"Uploading {filename}...")
        by_bot = self._bot

        size = os.path.getsize(file)
        if size < 5 * 2 ** 20:
            show_progress = False

        if use_cache and self._cache.get("upload_cache"):
            for cached in self._cache["upload_cache"]:
                if (
                    cached["size"] == size
                    and cached["path"] == path
                    and cached["name"] == filename
                    and cached["by_bot"] == by_bot
                ):
                    if to_delete:
                        with contextlib.suppress(FileNotFoundError):
                            os.remove(file)
                    return cached["raw_file"], time.time() - start_time

        from pyUltroid.fns.FastTelethon import upload_file
        from pyUltroid.fns.helper import progress

        progress_cb = None
        if show_progress and event is not None:
            def progress_cb(completed, total):  # noqa: WPS430
                asyncio.create_task(
                    progress(completed, total, event, start_time, message)
                )

        with open(file, "rb") as fp:
            raw_file = await upload_file(
                client=self,
                file=fp,
                filename=filename,
                progress_callback=progress_cb,
            )
        if not raw_file:
            raise RuntimeError(f"Failed to upload {filename!r} via FastTelethon.")

        cache_entry = {
            "by_bot": by_bot,
            "size": size,
            "path": path,
            "name": filename,
            "raw_file": raw_file,
        }
        self._cache.setdefault("upload_cache", []).append(cache_entry)

        if to_delete:
            with contextlib.suppress(FileNotFoundError):
                os.remove(file)
        return raw_file, time.time() - start_time

    async def fast_downloader(self, file, **kwargs):
        """Download ``file`` (a ``Document``) using parallel MTProto senders."""
        show_progress = kwargs.get("show_progress", False)
        filename = kwargs.get("filename") or ""
        event = kwargs.get("event") if show_progress else None
        if file.size < 10 * 2 ** 20:
            show_progress = False

        from pyUltroid.fns.FastTelethon import download_file
        from pyUltroid.fns.helper import progress

        start_time = time.time()
        if not filename:
            try:
                if isinstance(file.attributes[-1], DocumentAttributeFilename):
                    filename = file.attributes[-1].file_name
            except (IndexError, AttributeError):
                mimetype = getattr(file, "mime_type", "application/octet-stream")
                ext = mimetypes.guess_extension(mimetype) or ""
                filename = f"{mimetype.split('/')[0]}-{round(start_time)}{ext}"

        message = kwargs.get("message", f"Downloading {filename}...")

        progress_cb = None
        if show_progress and event is not None:
            def progress_cb(completed, total):  # noqa: WPS430
                asyncio.create_task(
                    progress(completed, total, event, start_time, message)
                )

        with open(filename, "wb") as fp:
            raw_file = await download_file(
                client=self,
                location=file,
                out=fp,
                progress_callback=progress_cb,
            )
        if not raw_file:
            raise RuntimeError(f"Failed to download {filename!r} via FastTelethon.")
        return raw_file, time.time() - start_time

    # ---------------------------------------------------- loop helpers
    def run_in_loop(self, coro):
        """Run ``coro`` to completion on the client's event loop."""
        return self.loop.run_until_complete(coro)

    def run(self) -> None:
        """Block until the client disconnects."""
        self.run_until_disconnected()

    def add_handler(self, func, *args, **kwargs) -> None:
        """Add an event handler, but ignore duplicate registrations."""
        if any(existing is func for existing, _ in self.list_event_handlers()):
            return
        self.add_event_handler(func, *args, **kwargs)

    # ---------------------------------------------------- convenience
    @property
    def utils(self):
        return telethon_utils

    @property
    def full_name(self) -> str:
        """Display name of the underlying account."""
        return telethon_utils.get_display_name(self.me)

    @property
    def uid(self) -> int:
        """The numeric Telegram ID of the underlying account."""
        return self.me.id

    async def parse_id(self, text):
        """Convert ``text`` (a username, id or link) into a peer id."""
        with contextlib.suppress(TypeError, ValueError):
            text = int(text)
        return await self.get_peer_id(text)
