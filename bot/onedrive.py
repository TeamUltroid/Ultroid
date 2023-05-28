import base64
import math
import os
import time
import traceback
from urllib.parse import parse_qs, urlencode

import aiohttp
from aiohttp import ClientSession
from utilities.helper import humanbytes, time_formatter

from database import udB


class Progress:
    def __init__(self, total, filename, filepath="resources/downloads"):
        self.filepath = filepath
        self.filename = filename
        self.total = total
        self.completed = 0
        self.start_time = time.time()
        self.last_update = time.time()

    async def update(self, chunk_size, event):
        self.completed += chunk_size
        self.remaining_bytes = self.total - self.completed
        self.percent = math.floor(self.completed / self.total * 100)
        self.speed = self.completed / (time.time() - self.start_time)
        self.eta = time_formatter(
            self.remaining_bytes / self.speed * 1000) if (self.speed > 0) else 0
        current_time = time.time()
        if (current_time - self.last_update) > 5:
            await event.edit(
                f"`Downloading ``{self.filename}`` from OneDrive\n\nStatus: {humanbytes(self.completed)}/{humanbytes(self.total)} [{self.percent}%]\nSpeed: {humanbytes(self.speed)}\nTime Elapsed: {time_formatter((current_time - self.start_time) * 1000)} [ETA: {self.eta}]`"
            ) if self.completed < self.total else None
            self.last_update = time.time()
        elif self.completed == self.total:
            await event.edit(
                f"Successfully downloaded {self.filename} to `{os.path.join(self.filepath, self.filename)}` in {time_formatter((current_time - self.start_time) * 1000)}\nSpeed:{humanbytes(self.total / (current_time - self.start_time))}/s"
            )


async def parallel_download(url, filename, chunk_size, filesize: int, event=None, file_path="resources/downloads"):
    try:
        progress = Progress(filesize, filename)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()

                # create new folder if not exists
                if not os.path.exists(file_path):
                    os.makedirs(file_path)

                with open(f"{file_path}/{filename}", "wb") as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await progress.update(len(chunk), event)
                        f.write(chunk)

    except Exception:
        print(traceback.format_exc())


class OneDrive:
    def __init__(self):
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.client_id = udB.get("OD_CLIENT_ID")
        self.client_secret = udB.get("OD_CLIENT_SECRET")
        self.creds = udB.get_key("OD_AUTH_TOKEN") or {}
        self.session = ClientSession()

    def get_oauth2_url(self):
        params = {
            "client_id": self.client_id,
            "scope": "offline_access Files.ReadWrite.All",
            "response_type": "code",
            "redirect_uri": "http://localhost",
        }
        return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{urlencode(params)}"

    async def get_access_token(self, code: str = None):
        if not code:
            return {"error": "No code provided"}
        if code.startswith("http://localhost"):
            code = parse_qs(code.split("?")[1]).get("code")[0]
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost",
        }
        async with self.session.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        ) as resp:
            self.creds = await resp.json()
            self.creds["expires_at"] = time.time() + self.creds["expires_in"]
            udB.set_key("OD_AUTH_TOKEN", self.creds)
            await resp.release()
            return self.creds

    async def refresh_access_token(self):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.creds.get("refresh_token"),
            "grant_type": "refresh_token",
            "redirect_uri": "http://localhost",
        }
        async with self.session.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        ) as resp:
            self.creds = await resp.json()
            self.creds["expires_at"] = time.time() + self.creds["expires_in"]
            await resp.release()
            udB.set_key("OD_AUTH_TOKEN", self.creds)
            return

    async def get_headers(self):
        if self.creds.get("expires_at", 0) < time.time():
            await self.refresh_access_token()
        return {
            "Authorization": f"Bearer {self.creds['access_token']}",
            "Content-Type": "application/json",
        }

    async def get_folder_id(self, folder_name: str):
        url = f"{self.base_url}/me/drive/root/children"
        async with self.session.get(
            url, headers=await self.get_headers()
        ) as resp:
            data = await resp.json()
            for item in data["value"]:
                if item["name"] == folder_name:
                    return item["id"]
            return None

    async def getshareablelink(self, file_id: str):
        url = f"{self.base_url}/me/drive/items/{file_id}/createLink"
        async with self.session.post(
            url, headers=await self.get_headers(), json={"type": "view", "scope": "anonymous"}
        ) as resp:
            data = await resp.json()
            await resp.release()
            return data["link"]["webUrl"]

    async def download_file(self, event, file_path: str, file_url):
        file_url = "u!" + base64.urlsafe_b64encode(file_url.encode()).decode()
        async with self.session.get(
            f"{self.base_url}/shares/{file_url}/driveItem",
            headers=await self.get_headers(),
        ) as resp:
            data = await resp.json()
            await resp.release()
            if data.get("error"):
                return await event.edit(data["error"]["message"])
        file_name = data["name"]
        file_size = int(data["size"])
        download_url = data["@microsoft.graph.downloadUrl"]
        chunk_size = 50 * 1024 * 1024 if file_size > 50 * \
            1024 * 1024 else 100 * 1024 * 1024
        # download file with parallel downloading
        await parallel_download(
            download_url,
            file_name,
            chunk_size,
            file_size,
            event
        )
        return file_name

    async def upload_file(self, event, file_path: str, folder_id: str = "root"):
        url = f"{self.base_url}/me/drive/items/{folder_id}:/{os.path.basename(file_path)}:/createUploadSession"
        async with self.session.post(
            url,
            headers=await self.get_headers(),
            json={
                "name": os.path.basename(file_path),
            },
        ) as resp:
            upload_url = (await resp.json())["uploadUrl"]
            await resp.release()
        chunksize = 50 * 1024 * 1024
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)
        start = time.time()
        last_txt = ""

        with open(file_path, "rb") as f:
            uploaded = 0
            start = time.time()
            resp = None
            while filesize != uploaded:
                chunk_data = f.read(chunksize)
                headers = {
                    "Content-Length": str(len(chunk_data)),
                    "Content-Range": "bytes "
                    + str(uploaded)
                    + "-"
                    + str(uploaded + len(chunk_data) - 1)
                    + "/"
                    + str(filesize),
                }
                uploaded += len(chunk_data)
                resp = await self.session.put(
                    upload_url, data=chunk_data, headers=headers
                )
                diff = time.time() - start
                percentage = round((uploaded / filesize) * 100, 2)
                speed = round(uploaded / diff, 2)
                eta = round((filesize - uploaded) / speed, 2) * 1000
                crnt_txt = (
                    f"`Uploading {filename} to GDrive...\n\n"
                    + f"Status: {humanbytes(uploaded)}/{humanbytes(filesize)} »» {percentage}%\n"
                    + f"Speed: {humanbytes(speed)}/s\n"
                    + f"ETA: {time_formatter(eta)}`"
                )
                if round((diff % 10.00) == 0) or last_txt != crnt_txt:
                    await event.edit(crnt_txt)
                    last_txt = crnt_txt
            data = await resp.json()
            data["shareUrl"] = await self.getshareablelink(data.get("id"))
            return data
