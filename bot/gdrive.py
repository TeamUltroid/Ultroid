# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import json
import logging
import os
import time
# from io import FileIO
from mimetypes import guess_type
from urllib.parse import parse_qs, urlencode

from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError

from database import udB

from .helper import humanbytes, time_formatter

# from apiclient.http import LOGGER, MediaFileUpload, MediaIoBaseDownload
# from googleapiclient.discovery import build, logger
# from googleapiclient.errors import ResumableUploadError
# from httplib2 import Http
# from oauth2client.client import OOB_CALLBACK_URN, OAuth2WebServerFlow
# from oauth2client.client import logger as _logger
# from oauth2client.file import Storage


# for log in [LOGGER, logger, _logger]:
#     log.setLevel(WARNING)

log = logging.getLogger("GDrive")

"""class GDriveManager:
    def __init__(self):
        self._flow = {}
        self.gdrive_creds = {
            "oauth_scope": [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/drive.metadata",
            ],
            "dir_mimetype": "application/vnd.google-apps.folder",
            "redirect_uri": OOB_CALLBACK_URN,
        }
        self.auth_token = udB.get_key("GDRIVE_AUTH_TOKEN")
        self.folder_id = udB.get_key("GDRIVE_FOLDER_ID")
        self.token_file = "resources/auth/gdrive_creds.json"

    @staticmethod
    def _create_download_link(fileId: str):
        return f"https://drive.google.com/uc?id={fileId}&export=download"

    @staticmethod
    def _create_folder_link(folderId: str):
        return f"https://drive.google.com/folderview?id={folderId}"

    def _create_token_file(self, code: str = None):
        if code and self._flow:
            _auth_flow = self._flow["_"]
            credentials = _auth_flow.step2_exchange(code)
            Storage(self.token_file).put(credentials)
            return udB.set_key("GDRIVE_AUTH_TOKEN", str(
                open(self.token_file).read()))
        try:
            _auth_flow = OAuth2WebServerFlow(
                udB.get_key("GDRIVE_CLIENT_ID")
                or "458306970678-jhfbv6o5sf1ar63o1ohp4c0grblp8qba.apps.googleusercontent.com",
                udB.get_key("GDRIVE_CLIENT_SECRET")
                or "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",
                self.gdrive_creds["oauth_scope"],
                redirect_uri=self.gdrive_creds["redirect_uri"],
            )
            self._flow["_"] = _auth_flow
        except KeyError:
            return "Fill GDRIVE client credentials"
        return _auth_flow.step1_get_authorize_url()

    @property
    def _http(self):
        storage = Storage(self.token_file)
        creds = storage.get()
        http = Http()
        http.redirect_codes = http.redirect_codes - {308}
        creds.refresh(http)
        return creds.authorize(http)

    @property
    def _build(self):
        return build("drive", "v3", http=self._http, cache_discovery=False)

    def _set_permissions(self, fileId: str):
        _permissions = {
            "role": "reader",
            "type": "anyone",
            "value": None,
            "withLink": True,
        }
        self._build.permissions().create(
            fileId=fileId, body=_permissions, supportsAllDrives=True
        ).execute(http=self._http)

    async def _upload_file(
        self, event, path: str, filename: str = None, folder_id: str = None
    ):
        last_txt = ""
        if not filename:
            filename = path.split("/")[-1]
        mime_type = guess_type(path)[0] or "application/octet-stream"
        media_body = MediaFileUpload(path, mimetype=mime_type, resumable=True)
        body = {
            "name": filename,
            "description": "Uploaded using Ultroid Userbot",
            "mimeType": mime_type,
        }
        if folder_id:
            body["parents"] = [folder_id]
        elif self.folder_id:
            body["parents"] = [self.folder_id]
        try:
            upload = self._build.files().create(
                body=body,
                media_body=media_body,
                fields="name, id, webContentLink",
                supportsAllDrives=True,
            )
            start = time.time()
            _status = None
            while not _status:
                _progress, _status = upload.next_chunk(num_retries=3)
                if _progress:
                    diff = time.time() - start
                    completed = _progress.resumable_progress
                    total_size = _progress.total_size
                    percentage = round((completed / total_size) * 100, 2)
                    speed = round(completed / diff, 2)
                    eta = round((total_size - completed) / speed, 2) * 1000
                    crnt_txt = (
                        f"`Uploading {filename} to GDrive...\n\n"
                        + f"Status: {humanbytes(completed)}/{humanbytes(total_size)} »» {percentage}%\n"
                        + f"Speed: {humanbytes(speed)}/s\n"
                        + f"ETA: {time_formatter(eta)}`"
                    )
                    if round((diff % 10.00) == 0) or last_txt != crnt_txt:
                        await event.edit(crnt_txt)
                        last_txt = crnt_txt
        except ResumableUploadError as err:
            if err.resp.status == 403:
                body["parents"] = ["root"]
                upload = self._build.files().create(
                    body=body,
                    media_body=media_body,
                    fields="name, id, webContentLink",
                    supportsAllDrives=True,
                )
                start = time.time()
                _status = None
                while not _status:
                    _progress, _status = upload.next_chunk(num_retries=3)
                    if _progress:
                        diff = time.time() - start
                        completed = _progress.resumable_progress
                        total_size = _progress.total_size
                        percentage = round((completed / total_size) * 100, 2)
                        speed = round(completed / diff, 2)
                        eta = round((total_size - completed) / speed, 2) * 1000
                        crnt_txt = (
                            f"`Uploading {filename} to GDrive...\n\n"
                            + f"Status: {humanbytes(completed)}/{humanbytes(total_size)} »» {percentage}%\n"
                            + f"Speed: {humanbytes(speed)}/s\n"
                            + f"ETA: {time_formatter(eta)}`"
                        )
                        if round((diff % 10.00) == 0) or last_txt != crnt_txt:
                            await event.edit(crnt_txt)
                            last_txt = crnt_txt
                if not folder_id:
                    folder_id = self.folder_id
                _status = await self._copy_file(
                    upload["id"], file_metadata["name"], folder_id, True
                )

        try:
            self._set_permissions(fileId=_status.get("id"))
        except BaseException:
            pass
        return _status.get("webContentLink")

    async def _download_file(self, event, fileId: str, filename: str = None):
        last_txt = ""
        if fileId.startswith("http"):
            if "=download" in fileId:
                fileId = fileId.split("=")[1][:-7]
            elif "/view" in fileId:
                fileId = fileId.split("/")[::-1][1]
        try:
            if not filename:
                filename = (
                    self._build.files()
                    .get(fileId=fileId, supportsAllDrives=True)
                    .execute()["name"]
                )
            downloader = self._build.files().get_media(
                fileId=fileId, supportsAllDrives=True
            )
        except Exception as ex:
            return False, str(ex)
        with FileIO(filename, "wb") as file:
            start = time.time()
            download = MediaIoBaseDownload(file, downloader)
            _status = None
            while not _status:
                _progress, _status = download.next_chunk(num_retries=3)
                if _progress:
                    diff = time.time() - start
                    completed = _progress.resumable_progress
                    total_size = _progress.total_size
                    percentage = round((completed / total_size) * 100, 2)
                    speed = round(completed / diff, 2)
                    eta = round((total_size - completed) / speed, 2) * 1000
                    crnt_txt = (
                        f"`Downloading {filename} from GDrive...\n\n"
                        + f"Status: {humanbytes(completed)}/{humanbytes(total_size)} »» {percentage}%\n"
                        + f"Speed: {humanbytes(speed)}/s\n"
                        + f"ETA: {time_formatter(eta)}`"
                    )
                    if round((diff % 10.00) == 0) or last_txt != crnt_txt:
                        await event.edit(crnt_txt)
                        last_txt = crnt_txt
        return True, filename

    async def _copy_file(
        self, fileId: str, filename: str, folder_id: str = None, move: bool = False
    ):
        file_metadata = {
            "name": filename,
            "description": "Copied via Ultroid",
        }
        if folder_id:
            file_metadata["parents"] = [folder_id]
        elif self.folder_id:
            file_metadata["parents"] = [folder_id]
        if move:
            del file_metadata["parents"]
            _status = (
                self._build.files()
                .update(
                    fileId=fileId,
                    body=file_metadata,
                    supportsAllDrives=True,
                    fields="name, id, webContentLink",
                    addParents=folder_id,
                    removeParents="root",
                )
                .execute()
            )
        else:
            _status = (
                self._build.files()
                .copy(
                    fileId=fileId,
                    body=file_metadata,
                    supportsAllDrives=True,
                    fields="name, id, webContentLink",
                )
                .execute()
            )
        return _status

    @property
    def _list_files(self):
        _items = (
            self._build.files()
            .list(
                supportsTeamDrives=True,
                includeTeamDriveItems=True,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=None,
            )
            .execute()
        )
        _files = {}
        for files in _items.get("files", []):
            if files["mimeType"] == self.gdrive_creds["dir_mimetype"]:
                _files[self._create_folder_link(files["id"])] = files["name"]
            else:
                _files[self._create_download_link(files["id"])] = files["name"]
        return _files

    def create_directory(self, directory):
        body = {
            "name": directory,
            "mimeType": self.gdrive_creds["dir_mimetype"],
        }
        if self.folder_id:
            body["parents"] = [self.folder_id]
        file = (
            self._build.files()
            .create(body=body, supportsAllDrives=True, fields="name, id")
            .execute()
        )
        fileId = file.get("id")
        self._set_permissions(fileId=fileId)
        return fileId

    def search(self, title):
        query = f"name contains '{title}' and trashed=false"
        if self.folder_id:
            query += f" and '{self.folder_id}' in parents"
        _items = (
            self._build.files()
            .list(
                supportsTeamDrives=True,
                includeTeamDriveItems=True,
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=None,
            )
            .execute()
        )
        return {
            files["name"]: self._create_download_link(files["id"])
            for files in _items["files"]
        }"""


# Assuming it works without any error
class GDrive:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/drive/v3"
        self._session = ClientSession()
        self.client_id = udB.get_key("GDRIVE_CLIENT_ID")
        self.client_secret = udB.get_key("GDRIVE_CLIENT_SECRET")
        self.folder_id = udB.get_key("GDRIVE_FOLDER_ID") or None
        self.scope = "https://www.googleapis.com/auth/drive"
        self.creds = udB.get_key("GDRIVE_AUTH_TOKEN") or {}
        self.headers = {
            "Authorization": "Bearer " + self.creds.get("access_token"),
            "Content-Type": "application/json",
        }

    def get_oauth2_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
            "client_id": self.client_id,
            "redirect_uri": "http://localhost",
            "response_type": "code",
            "scope": self.scope,
            "access_type": "offline",
        })

    async def get_access_token(self, code) -> dict:
        if code.startswith("http://localhost"):
            # get all url arguments
            code = parse_qs(code.split("?")[1]).get("code")[0]
        url = "https://oauth2.googleapis.com/token"
        resp = await self._session.post(url, data={"client_id": self.client_id, "client_secret": self.client_secret, "redirect_uri": "http://localhost", "grant_type": "authorization_code", "code": code}, headers={"Content-Type": "application/x-www-form-urlencoded"})
        self.creds = await resp.json()
        self.creds["expires_in"] = time.time() + 3590
        udB.set_key("GDRIVE_AUTH_TOKEN", self.creds)
        return self.creds

    async def refresh_access_token(self) -> None:
        resp = await self._session.post("https://oauth2.googleapis.com/token", data={"client_id": self.client_id, "client_secret": self.client_secret, "grant_type": "refresh_token", "refresh_token": self.creds.get("refresh_token")}, headers={"Content-Type": "application/x-www-form-urlencoded"})
        self.creds["access_token"] = (await resp.json())["access_token"]
        self.creds["expires_in"] = time.time() + 3590
        self.headers = {
            "Authorization": "Bearer " + self.creds.get("access_token"),
            "Content-Type": "application/json",
        }
        udB.set_key("GDRIVE_AUTH_TOKEN", self.creds)

    async def get_size_status(self) -> dict:
        """returns
        {
            "limit": "16106127360",
            "usage": "18896",
            "usageInDrive": "18896",
            "usageInDriveTrash": "0",
        }"""
        await self.refresh_access_token() if time.time() > self.creds.get("expires_in") else None
        return await (await self._session.get(
            self.base_url + "/about",
            headers=self.headers,
            params={"fields": "storageQuota"},
        )).json()["storageQuota"]

    async def set_permissions(self, fileid: str, role: str = "reader", type: str = "anyone"):
        # set permissions to anyone with link can view
        await self.refresh_access_token() if time() > self.creds.get("expires_in") else None
        return await (await self._session.post(
            self.base_url + f"/files/{fileid}/permissions",
            headers=self.headers,
            json={
                "role": role,
                "type": type,
            },
        )).json()

    async def list_files(self) -> dict:
        await self.refresh_access_token() if time.time() > self.creds.get("expires_in") else None
        return await (await self._session.get(
            self.base_url + "/files",
            headers=self.headers,
        )).json()

    async def delete(self, fileId: str) -> dict:
        await self.refresh_access_token() if time.time() > self.creds.get("expires_in") else None
        r = await self._session.delete(
            self.base_url + f"/files/{fileId}",
            headers=self.headers,
        )
        try:
            return await r.json()
        except ContentTypeError:
            return {"status": "success"}

    async def copy_file(self, fileId: str, filename: str, folder_id: str, move: bool = False):
        await self.refresh_access_token() if time.time() > self.creds.get("expires_in") else None
        update_url = self.base_url + f"/files/{fileId}"
        params = {
            "name": filename,
            "mimeType": "application/octet-stream",
            "fields": "id, name, webContentLink",
            "supportsAllDrives": True,
        }
        file_metadata = {
            "name": filename,
            "fileId": fileId,
        }
        params["addParents"] = folder_id if folder_id else self.folder_id
        params["removeParents"] = "root" if move else None
        r = await self._session.patch(
            update_url,
            headers=self.headers,
            data=json.dumps(file_metadata),
            params=params,
        )
        r = await r.json()
        if r.get("error") and r["error"]["code"] == 401:
            await self.refresh_access_token()
            return await self.copy_file(fileId, filename, folder_id, move)
        return r

    async def upload_file(self, event, path: str, filename: str = None, folder_id: str = None):
        await self.refresh_access_token() if time.time() > self.creds.get("expires_in") else None
        last_txt = ""
        filename = filename if filename else path.split("/")[-1]
        mime_type = guess_type(path)[0] or "application/octet-stream"
        # upload with progress bar
        filesize = os.path.getsize(path)
        usage = await self.get_size_status()
        if filesize > (int(usage["limit"]) - int(usage["usage"])):
            return  # hurrr
        chunksize = 104857600  # 100MB
        params = {
            "name": filename,
            "mimeType": mime_type,
            "fields": "id, name, webContentLink",
            "parents": [folder_id] if folder_id else [self.folder_id],
        }
        r = await self._session.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true",
            headers=self.headers,
            data=json.dumps(params),
            params={"fields": "id, name, webContentLink"},
        )
        if r.status == 401:
            await self.refresh_access_token()
            return await self.upload_file(event, path, filename, folder_id)
        elif r.status == 403:
            # upload to root and move
            r = await self.upload_file(event, path, filename, "root")
            return await self.copy_file(r["id"], filename, folder_id, move=True)
        upload_url = r.headers.get("Location")

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
