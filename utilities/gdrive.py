# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import base64
import json
import logging
import os
import time

from mimetypes import guess_type
from urllib.parse import parse_qs, urlencode

from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError

from database import udB

from .helper import humanbytes, time_formatter

try:
    import jwt
except BaseException:
    pass


log = logging.getLogger("GDrive")

# Assuming it works without any error


class GDrive:
    def __init__(self):
        self._session = ClientSession()
        self.base_url: str = "https://www.googleapis.com/drive/v3"
        self.client_id: str = udB.get_key("GDRIVE_CLIENT_ID")
        self.client_secret: str = udB.get_key("GDRIVE_CLIENT_SECRET")
        self.folder_id: str = udB.get_key("GDRIVE_FOLDER_ID") or "root"
        self.redirect_uri: str = udB.get_key("GDRIVE_REDIRECT_URI") or "http://localhost"
        self.scope: str = "https://www.googleapis.com/auth/drive"
        self.creds: dict = udB.get_key("GDRIVE_AUTH_TOKEN") or {}
        self.service_account: dict = udB.get_key("GDRIVE_SERVICE_KEY")
        self.folder_mime: str = "application/vnd.google-apps.folder"

    @staticmethod
    def _create_download_link(file_id: str) -> str:
        return f"https://drive.google.com/uc?id={file_id}&export=download"

    @staticmethod
    def _create_folder_link(folder_id: str) -> str:
        return f"https://drive.google.com/folderview?id={folder_id}"

    def get_oauth2_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "access_type": "offline",
        })

    async def get_access_token(self, code: str = None) -> dict:
        if self.service_account:
            header = {
                "alg": "RS256",
                "typ": "JWT"
            }
            payload = {
                "iss": self.service_account["client_email"],
                "scope": self.scope,
                "aud": "https://oauth2.googleapis.com/token",
                "exp": int(time.time()) + 3590,
                "iat": int(time.time())
            }
            token = jwt.encode(payload, self.service_account.get("private_key"), algorithm="RS256", headers=header)
            resp = await self._session.post("https://oauth2.googleapis.com/token", data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": token})
            self.creds = await resp.json()
            self.creds["expires_in"] = time.time() + 3590
            udB.set_key("GDRIVE_AUTH_TOKEN", self.creds)
            return self.creds
        resp = await self._session.post(
            "https://oauth2.googleapis.com/token",
            data={"client_id": self.client_id, "client_secret": self.client_secret, "redirect_uri": self.redirect_uri, "grant_type": "authorization_code", "code": code}, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        self.creds = await resp.json()
        self.creds["expires_in"] = time.time() + 3590
        udB.set_key("GDRIVE_AUTH_TOKEN", self.creds)
        return self.creds

    async def _refresh_access_token(self) -> None:
        if self.service_account:
            header = {
                "alg": "RS256",
                "typ": "JWT"
            }
            payload = {
                "iss": self.service_account["client_email"],
                "scope": self.scope,
                "aud": "https://oauth2.googleapis.com/token",
                "exp": int(time.time()) + 3600,
                "iat": int(time.time())
            }
            token = jwt.encode(payload, self.service_account.get("private_key"), algorithm="RS256", headers=header)
            resp = await self._session.post("https://oauth2.googleapis.com/token", data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": token})
            self.creds = await resp.json()
            self.creds["expires_in"] = time.time() + 3590
            udB.set_key("GDRIVE_AUTH_TOKEN", self.creds)
            return
        resp = await self._session.post("https://oauth2.googleapis.com/token", data={"client_id": self.client_id, "client_secret": self.client_secret, "grant_type": "refresh_token", "refresh_token": self.creds.get("refresh_token")}, headers={"Content-Type": "application/x-www-form-urlencoded"})
        creds = await resp.json()
        if "error" in creds:
            return creds
        self.creds["access_token"] = creds["access_token"]
        self.creds["expires_in"] = time.time() + 3590
        udB.set_key("GDRIVE_AUTH_TOKEN", self.creds)

    async def get_size_status(self) -> dict:
        await self._refresh_access_token() if time.time() > self.creds.get("expires_in") else None
        return await (await self._session.get(
            self.base_url + "/about",
            headers={
                "Authorization": "Bearer " + self.creds.get("access_token"),
                "Content-Type": "application/json",
            },
            params={"fields": "storageQuota"},
        )).json()

    async def set_permissions(self, fileid: str, role: str = "reader", type: str = "anyone"):
        # set permissions to anyone with link can view
        await self._refresh_access_token() if time.time() > self.creds.get("expires_in") else None
        return await (await self._session.post(
            self.base_url + f"/files/{fileid}/permissions",
            headers={
                "Authorization": "Bearer " + self.creds.get("access_token"),
                "Content-Type": "application/json",
            },
            json={
                "role": role,
                "type": type,
            },
        )).json()

    async def list_files(self) -> list:
        await self._refresh_access_token() if time.time() > self.creds.get("expires_in") else None
        files = []
        page_token = None
        params = {"supportAllDrives": "true"}
        while True:
            resp = await (await self._session.get(
                self.base_url + "/files",
                headers={
                   "Authorization": "Bearer " + self.creds.get("access_token"),
                   "Content-Type": "application/json",
                },
                params=params,
            )).json()
            for file in resp.get("files", []):
                if file["mimeType"] == self.folder_mime:
                    file["url"] = self._create_folder_link(file["id"])
                else:
                    file["url"] = self._create_download_link(file["id"])
                files.append(file)
            page_token = resp.get("nextPageToken", None)
            if page_token is None:
                break
            else:
                params["pageToken"] = page_token
        return files

    async def delete(self, fileId: str) -> dict:
        await self._refresh_access_token() if time.time() > self.creds.get("expires_in") else None
        r = await self._session.delete(
            self.base_url + f"/files/{fileId}",
            headers={
                "Authorization": "Bearer " + self.creds.get("access_token"),
                "Content-Type": "application/json",
            },
        )
        try:
            return await r.json()
        except ContentTypeError:
            return {"status": "success"}

    async def copy_file(self, fileId: str, filename: str, folder_id: str, move: bool = False):
        await self._refresh_access_token() if time.time() > self.creds.get("expires_in") else None
        headers = {
            "Authorization": "Bearer " + self.creds.get("access_token"),
            "Content-Type": "application/json",
        }
        params = {
            "name": filename,
            "mimeType": "application/octet-stream",
            "fields": "id, name, webContentLink",
            "supportsAllDrives": "true",
        }
        file_metadata = {
            "name": filename,
            "fileId": fileId,
        }
        if folder_id:
            file_metadata["parents"] = [folder_id]
        elif self.folder_id:
            file_metadata["parents"] = [self.folder_id]
        params["addParents"] = folder_id if folder_id else self.folder_id
        params["removeParents"] = "root" if move else None
        r = await self._session.patch(
            self.base_url + f"/files/{fileId}",
            headers=headers,
            data=json.dumps(file_metadata),
            params=params,
        )
        r = await r.json()
        if r.get("error") and r["error"]["code"] == 401:
            await self.refresh_access_token()
            return await self.copy_file(fileId, filename, folder_id, move)
        return r

    async def upload_file(self, event, path: str, filename: str = None, folder_id: str = None):
        await self._refresh_access_token() if time.time() > self.creds.get("expires_in") else None
        last_txt = ""
        filename = filename if filename else path.split("/")[-1]
        mime_type = guess_type(path)[0] or "application/octet-stream"
        # upload with progress bar
        filesize = os.path.getsize(path)
        # await self.get_size_status()
        chunksize = 104857600  # 100MB
        # 1. Retrieve session for resumable upload.
        headers = {"Authorization": "Bearer " +
                   self.creds.get("access_token"), "Content-Type": "application/json"}
        params = {
            "name": filename,
            "mimeType": mime_type,
            "fields": "id, name, webContentLink",
            "parents": [folder_id] if folder_id else [self.folder_id],
        }
        r = await self._session.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
            headers=headers,
            data=json.dumps(params),
            params={"fields": "id, name, webContentLink"},
        )
        if r.status == 401:
            await self._refresh_access_token()
            return await self.upload_file(event, path, filename, folder_id)
        elif r.status == 403:
            # upload to root and move
            r = await self.upload_file(event, path, filename, "root")
            return await self.copy_file(r["id"], filename, folder_id, move=True)
        upload_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&upload_id=" + \
            r.headers.get("X-GUploader-UploadID")

        with open(path, "rb") as f:
            uploaded = 0
            start = time.time()
            resp = None
            while filesize != uploaded:
                chunk_data = f.read(chunksize)
                headers = {"Content-Length": str(len(chunk_data)),
                           "Content-Range": "bytes " + str(uploaded) + "-" + str(uploaded + len(chunk_data) - 1) + "/" + str(filesize)}
                uploaded += len(chunk_data)
                resp = await self._session.put(upload_url, data=chunk_data, headers=headers)
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
            return await resp.json()
