import os
import time
from urllib.parse import urlencode

from aiohttp import ClientSession

from database import udB


class OneDrive:
    def __init__(self, session):
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.client_id = udB.get("OD_CLIENT_ID")
        self.client_secret = udB.get("OD_CLIENT_SECRET")
        self.creds = udB.get("OD_AUTH_TOKEN") or {}
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
            await resp.release()
            udB.set_key("OD_AUTH_TOKEN", self.creds)
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
            url, headers=await self.get_headers(), json={"type": "view"}
        ) as resp:
            data = await resp.json()
            await resp.release()
            return data["link"]["webUrl"]

    async def upload_file(self, file_path: str, folder_id: str = "root"):
        # create upload session
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
                    + f"Status: {uploaded}/{filesize} »» {percentage}%\n"
                    + f"Speed: {speed}/s\n"
                    + f"ETA: {eta}`"
                )
                if round((diff % 10.00) == 0) or last_txt != crnt_txt:
                    await event.edit(crnt_txt)
                    last_txt = crnt_txt
            return await resp.json()
