import asyncio
import base64
import concurrent.futures
import os
import time
from urllib.parse import parse_qs, urlencode

import aiohttp
from aiohttp import ClientSession
from utilities.helper import humanbytes, time_formatter

from database import udB

pquit = False


async def parallel_download(url, filename, chunk_size, filesize, event=None):
    chunks = range(0, filesize, chunk_size)

    the_iter = [[{
        "Range": "bytes=" + str(start) + "-" + str(start + chunk_size - 1)
    }, f"{filename}.part{i}"] for i, start in enumerate(
        chunks)]

    def run_async(func, *args):
        return asyncio.get_event_loop().run_until_complete(func(*args))

    async def download_part(arg):
        while not pquit:
            headers, partfile = arg
            async with aiohttp.request('GET', url, headers=headers) as response:

                chunk_size = 1024 * 1024 * 5

                size = 0
                with open(partfile, 'wb') as f:
                    # write to file
                    async for chunk in response.content.iter_chunked(chunk_size):
                        if not chunk:
                            break
                        f.write(chunk)
                        size += len(chunk)
                return size

    starttime = time.time()
    completed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        tasks = [executor.submit(run_async, download_part, i)
                 for i in the_iter]
        for future in concurrent.futures.as_completed(tasks):
            # todo
            if not event:
                return
            completed += future.result()
            speed = completed / (time.time() - starttime)
            percentage = completed * 100 / filesize
            eta = (filesize - completed) / speed
            progress = "[{0}{1}] \nP: {2}%\n".format(
                ''.join(["■" for i in range(math.floor(percentage / 5))]),
                ''.join(["▨" for i in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2))
            tmp = progress + "S: {0}/s\nETA: {1}".format(
                humanbytes(speed),
                time_formatter(eta))
            await event.edit(f"`{tmp}`")

    with open(f"resources/downloads/{filename}", 'wb') as mergedfile:
        for i in len(chunks):
            chunk_path = f"resources/tmp/{filename}.part{i}"
            with open(chunk_path, 'rb') as s:
                mergedfile.write(s.read())
            os.remove(chunk_path)

    return filename


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
        # file_url =
        # https://techierror-my.sharepoint.com/:u:/g/personal/techierror_techierror_onmicrosoft_com/EX8lAMP8pApLgzABaHCQTpgB39DUNTCrtkUftcTOGVPI7A
        file_url = "u!" + base64.urlsafe_b64encode(file_url.encode()).decode()
        async with self.session.get(
            f"{self.base_url}/shares/{file_url}/driveItem",
            headers=await self.get_headers(),
        ) as resp:
            data = await resp.json()
            await resp.release()
        file_name = data["name"]
        file_size = data["size"]
        download_url = data["@microsoft.graph.downloadUrl"]
        # download file with parallel downloading
        await parallel_download(
            download_url,
            file_path + "/" + file_name,
            file_name,
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
