# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import contextlib
import json
import math
import os
import random
import re
import secrets
import ssl
from io import BytesIO
from json.decoder import JSONDecodeError
from traceback import format_exc

from urllib.parse import urlparse
from core import *
from core.remote import Remote
from . import some_random_headers
from .helper import async_searcher, bash, run_async, fetch_sync, time_formatter

try:
    import certifi
except ImportError:
    certifi = None

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image, ImageDraw, ImageFont = None, None, None
    LOGS.info("PIL not installed!")

from urllib.parse import quote, unquote

from telethon import Button
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo


try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# ~~~~~~~~~~~~~~~~~~~~OFOX API~~~~~~~~~~~~~~~~~~~~
# @buddhhu


async def get_ofox(codename):
    ofox_baseurl = "https://api.orangefox.download/v3/"
    releases = await async_searcher(
        ofox_baseurl + "releases?codename=" + codename, re_json=True
    )
    device = await async_searcher(
        ofox_baseurl + "devices/get?codename=" + codename, re_json=True
    )
    return device, releases


# ~~~~~~~~~~~~~~~JSON Parser~~~~~~~~~~~~~~~
# @buddhhu


def _unquote_text(text):
    return text.replace("'", unquote("%5C%27")).replace('"', unquote("%5C%22"))


def json_parser(data, indent=None, ascii=False):
    parsed = {}
    try:
        if isinstance(data, str):
            parsed = json.loads(data)
        elif isinstance(data, dict):
            parsed = data
        elif hasattr(data, "to_json"):
            parsed = data.to_json()
        else:
            return
        if indent or ascii:
            parsed = json.dumps(parsed, indent=indent, ensure_ascii=ascii)
    except JSONDecodeError:
        parsed = eval(data)
    return parsed


# ~~~~~~~~~~~~~~~~Link Checker~~~~~~~~~~~~~~~~~


async def is_url_ok(url: str, shallow: bool = False):
    if shallow:
        parse = urlparse(url)
        return parse.netloc and parse.scheme
    try:
        await async_searcher(url, method="HEAD")
        return True
    except BaseException as er:
        LOGS.error(er)
    return False


# ~~~~~~~~~~~~~~~~ Metadata ~~~~~~~~~~~~~~~~~~~~


async def metadata(file):
    out, _ = await bash(f'mediainfo "{_unquote_text(file)}" --Output=JSON')
    if _ and _.endswith("NOT_FOUND"):
        raise Exception(
            f"'{_}' is not installed!\nInstall it to use this command."
        )
    data = {}
    _info = json.loads(out)["media"]["track"]
    info = _info[0]
    if info.get("Format") in ["GIF", "PNG"]:
        return {
            "height": _info[1]["Height"],
            "width": _info[1]["Width"],
            "bitrate": _info[1].get("BitRate", 320),
        }
    if info.get("AudioCount"):
        data["title"] = info.get("Title", file)
        data["performer"] = info.get("Performer") or udB.get_key("artist") or ""
    if info.get("VideoCount"):
        data["height"] = int(float(_info[1].get("Height", 720)))
        data["width"] = int(float(_info[1].get("Width", 1280)))
        data["bitrate"] = int(_info[1].get("BitRate", 320))
    data["duration"] = int(float(info.get("Duration", 0)))
    return data


# ~~~~~~~~~~~~~~~~ Attributes ~~~~~~~~~~~~~~~~


async def set_attributes(file):
    data = await metadata(file)
    if not data:
        return None
    if "width" in data:
        return [
            DocumentAttributeVideo(
                duration=data.get("duration", 0),
                w=data.get("width", 512),
                h=data.get("height", 512),
                supports_streaming=True,
            )
        ]
    ext = "." + file.split(".")[-1]
    return [
        DocumentAttributeAudio(
            duration=data.get("duration", 0),
            title=data.get("title", file.split("/")[-1].replace(ext, "")),
            performer=data.get("performer"),
        )
    ]


# ~~~~~~~~~~~~~~~~ Button stuffs ~~~~~~~~~~~~~~~


def get_msg_button(texts: str):
    btn = []
    for z in re.findall("\\[(.*?)\\|(.*?)\\]", texts):
        text, url = z
        urls = url.split("|")
        url = urls[0]
        if len(urls) > 1:
            btn[-1].append([text, url])
        else:
            btn.append([[text, url]])

    txt = texts
    for z in re.findall("\\[.+?\\|.+?\\]", texts):
        txt = txt.replace(z, "")

    return txt.strip(), btn


def create_tl_btn(button: list):
    btn = []
    for z in button:
        if len(z) > 1:
            kk = [Button.url(x, y.strip()) for x, y in z]
            btn.append(kk)
        else:
            btn.append([Button.url(z[0][0], z[0][1].strip())])
    return btn


def format_btn(buttons: list):
    txt = ""
    for i in buttons:
        a = 0
        for i in i:
            if hasattr(i.button, "url"):
                a += 1
                if a > 1:
                    txt += f"[{i.button.text} | {i.button.url} | same]"
                else:
                    txt += f"[{i.button.text} | {i.button.url}]"
    _, btn = get_msg_button(txt)
    return btn


# ~~~~~~~~~~~~~~~Saavn Downloader~~~~~~~~~~~~~~~
# @techierror


async def saavn_search(query: str):
    try:
        data = await async_searcher(
            url=f"https://saavn-api.vercel.app/search/{query.replace(' ', '%20')}",
            re_json=True,
        )
    except BaseException:
        data = None
    return data


# --- webupload ------#
# @buddhhu

_webupload_cache = {}


async def webuploader(chat_id: int, msg_id: int, uploader: str):
    file = _webupload_cache[int(chat_id)][int(msg_id)]
    sites = {
        "anonfiles": {"url": "https://api.anonfiles.com/upload", "json": True},
        "siasky": {"url": "https://siasky.net/skynet/skyfile", "json": True},
        "file.io": {"url": "https://file.io", "json": True},
        "bayfiles": {"url": "https://api.bayfiles.com/upload", "json": True},
        "x0.at": {"url": "https://x0.at/", "json": False},
        "transfer": {"url": "https://transfer.sh", "json": False},
    }
    if uploader and uploader in sites:
        url = sites[uploader]["url"]
        json = sites[uploader]["json"]
    with open(file, "rb") as data:
        # todo: add progress bar
        status = await async_searcher(
            url, data={"file": data.read()}, post=True, re_json=json
        )
    if isinstance(status, dict):
        if "skylink" in status:
            return f"https://siasky.net/{status['skylink']}"
        if status["status"] == 200 or status["status"] is True:
            try:
                link = status["link"]
            except KeyError:
                link = status["data"]["file"]["url"]["short"]
            return link
    del _webupload_cache[int(chat_id)][int(msg_id)]
    return status


def text_set(text):
    lines = []
    if len(text) <= 55:
        lines.append(text)
    else:
        all_lines = text.split("\n")
        for line in all_lines:
            if len(line) <= 55:
                lines.append(line)
            else:
                k = len(line) // 55
                for z in range(1, k + 2):
                    lines.append(line[((z - 1) * 55) : (z * 55)])
    return lines[:25]


# --------------------------------------
# https://stackoverflow.com/a/74563494


async def get_google_images(query):
    soup = BeautifulSoup(
        await async_searcher(
            "https://google.com/search",
            params={"q": query, "tbm": "isch"},
            headers={"User-Agent": random.choice(some_random_headers)},
        ),
        "lxml",
    )
    google_images = []
    all_script_tags = soup.select("script")
    matched_images_data = "".join(
        re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags))
    )
    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)
    matched_google_image_data = re.findall(
        r"\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}", matched_images_data_json
    )
    matched_google_images_thumbnails = ", ".join(
        re.findall(
            r"\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]",
            str(matched_google_image_data),
        )
    ).split(", ")
    thumbnails = [
        bytes(bytes(thumbnail, "ascii").decode("unicode-escape"), "ascii").decode(
            "unicode-escape"
        )
        for thumbnail in matched_google_images_thumbnails
    ]
    removed_matched_google_images_thumbnails = re.sub(
        r"\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]",
        "",
        str(matched_google_image_data),
    )
    matched_google_full_resolution_images = re.findall(
        r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
        removed_matched_google_images_thumbnails,
    )
    full_res_images = [
        bytes(bytes(img, "ascii").decode("unicode-escape"), "ascii").decode(
            "unicode-escape"
        )
        for img in matched_google_full_resolution_images
    ]
    for index, (metadata, thumbnail, original) in enumerate(
        zip(soup.select(".isv-r.PNCib.MSM1fd.BUooTd"), thumbnails, full_res_images),
        start=1,
    ):
        google_images.append(
            {
                "title": metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")[
                    "title"
                ],
                "link": metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")[
                    "href"
                ],
                "source": metadata.select_one(".fxgdke").text,
                "thumbnail": thumbnail,
                "original": original,
            }
        )
    random.shuffle(google_images)
    return google_images


# Thanks https://t.me/KukiUpdates/23 for ChatBotApi


async def get_chatbot_reply(message):
    chatbot_base = "https://kuki-api-lac.vercel.app/message={}"
    req_link = chatbot_base.format(
        message,
    )
    try:
        return (await async_searcher(req_link, re_json=True)).get("reply")
    except Exception:
        LOGS.info(f"**ERROR:**`{format_exc()}`")


def check_filename(filroid):
    if os.path.exists(filroid):
        no = 1
        while True:
            ult = "{0}_{2}{1}".format(*os.path.splitext(filroid) + (no,))
            if os.path.exists(ult):
                no += 1
            else:
                return ult
    return filroid


# ------ Audio \\ Video tools funcn --------#

async def generate_screenshot(file):
    duration = (await metadata(file)).get("duration", 0) // 4
    _time = time_formatter(duration*1000)
    filename = file.split(".")
    filename.pop(-1)
    filename = ".".join(filename)
    await bash(f"ffmpeg -ss {_time} -i {file} -vframes 1 -q:v 1 {filename}.jpg -y")
    return filename + ".jpg"


# https://github.com/1Danish-00/CompressorBot/blob/main/helper/funcn.py#L104



async def genss(file):
    return (await metadata(file)).get("duration")


async def duration_s(file, stime):
    tsec = await genss(file)
    x = round(tsec / 5)
    y = round(tsec / 5 + int(stime))
    pin = stdr(x)
    pon = stdr(y) if y < tsec else stdr(tsec)
    return pin, pon


def stdr(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if len(str(minutes)) == 1:
        minutes = f"0{str(minutes)}"
    if len(str(hours)) == 1:
        hours = f"0{str(hours)}"
    if len(str(seconds)) == 1:
        seconds = f"0{str(seconds)}"
    return (
        (f"{str(hours)}:" if hours else "00:")
        + (f"{str(minutes)}:" if minutes else "00:")
        + ((str(seconds)) if seconds else "")
    )


# ------------------- used in pdftools --------------------#

# https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example


def order_points(pts):
    "get the required points"
    import numpy as np

    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def four_point_transform(image, pts):
    try:
        import cv2
    except ImportError:
        raise Exception("This function needs 'cv2' to be installed.")
    import numpy as np
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array(
        [[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]],
        dtype="float32",
    )
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (maxWidth, maxHeight))


async def Carbon(
    code,
    base_url="https://carbonara.solopov.dev/api/cook",
    file_name="ultroid",
    download=False,
    rayso=False,
    **kwargs,
):
    if rayso:
        base_url = (
            base_url
            if "/generate" in base_url
            else "https://rayso-api-desvhu-33.koyeb.app/generate"
        )
        kwargs["text"] = code
        kwargs["theme"] = kwargs.get("theme", "breeze")
        kwargs["darkMode"] = kwargs.get("darkMode", True)
        kwargs["title"] = kwargs.get("title", "Ultroid")
    else:
        kwargs["code"] = code

    def eval_(req):
        if req.headers["content-type"] != "image/png":
            try:
                return req.json()
            except Exception:
                return {"error": req.text}
        return req.content

    con = await async_searcher(base_url, method="POST", json=kwargs, evaluate=eval_)
    with contextlib.suppress(Exception):
        return con if isinstance(con, dict) else json_parser(con.decode())
    if not download:
        file = BytesIO(con)
        file.name = f"{file_name}.jpg"
    else:
        file = f"{file_name}.jpg"
        with open(file, "wb") as f:
            f.write(con)
    return file


# async def get_file_link(msg):
#     TODO: move to filestore plugin
#     from core import udB

#     msg_id = await msg.forward_to(udB.get_config("LOG_CHANNEL"))
#     await msg_id.reply(
#         "**Message has been stored to generate a shareable link. Do not delete it.**"
#     )
#     msg_id = msg_id.id
#     msg_hash = secrets.token_hex(nbytes=8)
#     store_msg(msg_hash, msg_id)
#     return msg_hash


def translate(text, target="en", detect=False):
    x = fetch_sync(
        f"{Remote.REMOTE_URL}/translate",
        json={"text": text, "target": target},
        re_json=True, method="POST"
    )
    if not x:
        return None
    res = x[0]
    text = res["translatedText"].replace("\ N", "\n").replace("\\n", "\n").replace("<br>", "\n")
    return (text, res["detectedSourceLanguage"]) if detect else text

atranslate = run_async(translate)



# ------------------------#


class LottieException(Exception):
    ...


class TgConverter:
    """Convert files related to Telegram"""

    @staticmethod
    async def animated_sticker(file, out_path="sticker.tgs", throw=False, remove=False):
        """Convert to/from animated sticker."""
        if out_path.endswith("webp"):
            er, out = await bash(
                f"lottie_convert.py --webp-quality 100 --webp-skip-frames 100 '{file}' '{out_path}'"
            )
        else:
            er, out = await bash(f"lottie_convert.py '{file}' '{out_path}'")
        if er and throw:
            raise LottieException(er)
        if remove:
            os.remove(file)
        if os.path.exists(out_path):
            return out_path

    @staticmethod
    async def animated_to_gif(file, out_path="gif.gif"):
        """Convert animated sticker to gif."""
        await bash(
            f"lottie_convert.py '{_unquote_text(file)}' '{_unquote_text(out_path)}'"
        )
        return out_path

    @staticmethod
    async def ffmpeg_convert(input_, output, remove=False):
        if output.endswith(".webm"):
            return await TgConverter.create_webm(
                input_, name=output[:-5], remove=remove
            )
        if output.endswith(".gif"):
            await bash(f"ffmpeg -i '{input_}' -an -sn -c:v copy '{output}.mp4' -y")
        else:
            await bash(f"ffmpeg -i '{input_}' '{output}' -y")
        if remove:
            os.remove(input_)
        if os.path.exists(output):
            return output

    @staticmethod
    async def create_webm(file, name="video", remove=False):
        _ = await metadata(file)
        name += ".webm"
        h, w = _["height"], _["width"]
        if h == w and h != 512:
            h, w = 512, 512
        if h != 512 or w != 512:
            if h > w:
                h, w = 512, -1
            if w > h:
                h, w = -1, 512
        await bash(
            f'ffmpeg -i "{file}" -preset fast -an -to 00:00:03 -crf 30 -bufsize 256k -b:v {_["bitrate"]} -vf "scale={w}:{h},fps=30" -c:v libvpx-vp9 "{name}" -y'
        )
        if remove:
            os.remove(file)
        return name

    @staticmethod
    def to_image(input_, name, remove=False):
        try:
            import cv2
        except ImportError:
            raise Exception("This function needs 'cv2' to be installed.")
        img = cv2.VideoCapture(input_)
        ult, roid = img.read()
        cv2.imwrite(name, roid)
        if remove:
            os.remove(input_)
        return name

    @staticmethod
    async def convert(
        input_file,
        outname="converted",
        convert_to=None,
        allowed_formats=[],
        remove_old=True,
    ):
        if "." in input_file:
            ext = input_file.split(".")[-1].lower()
        else:
            return input_file

        if (
            ext in allowed_formats
            or ext == convert_to
            or not (convert_to or allowed_formats)
        ):
            return input_file

        def recycle_type(exte):
            return convert_to == exte or exte in allowed_formats

        # Sticker to Something
        if ext == "tgs":
            for extn in ["webp", "json", "png", "mp4", "gif"]:
                if recycle_type(extn):
                    name = outname + "." + extn
                    return await TgConverter.animated_sticker(
                        input_file, name, remove=remove_old
                    )
            if recycle_type("webm"):
                input_file = await TgConverter.convert(
                    input_file, convert_to="gif", remove_old=remove_old
                )
                return await TgConverter.create_webm(input_file, outname, remove=True)
        # Json -> Tgs
        elif ext == "json":
            if recycle_type("tgs"):
                name = outname + ".tgs"
                return await TgConverter.animated_sticker(
                    input_file, name, remove=remove_old
                )
        # Video to Something
        elif ext in ["webm", "mp4", "gif"]:
            for exte in ["webm", "mp4", "gif"]:
                if recycle_type(exte):
                    name = outname + "." + exte
                    return await TgConverter.ffmpeg_convert(
                        input_file, name, remove=remove_old
                    )
            for exte in ["png", "jpg", "jpeg", "webp"]:
                if recycle_type(exte):
                    name = outname + "." + exte
                    return TgConverter.to_image(input_file, name, remove=remove_old)
        # Image to Something
        elif ext in ["jpg", "jpeg", "png", "webp"]:
            for extn in ["png", "webp", "ico"]:
                if recycle_type(extn):
                    img = Image.open(input_file)
                    name = outname + "." + extn
                    img.save(name, extn.upper())
                    if remove_old:
                        os.remove(input_file)
                    return name
            for extn in ["webm", "gif", "mp4"]:
                if recycle_type(extn):
                    name = outname + "." + extn
                    if extn == "webm":
                        input_file = await TgConverter.convert(
                            input_file,
                            convert_to="png",
                            remove_old=remove_old,
                        )
                    return await TgConverter.ffmpeg_convert(
                        input_file, name, remove=True if extn == "webm" else remove_old
                    )


def _get_value(stri):
    value = stri.strip()
    try:
        value = eval(value)
    except Exception as er:
        from core import LOGS

        LOGS.debug(er)
    return value


def safe_load(file, *args, **kwargs):
    read = file.split("\n") if isinstance(file, str) else file.readlines()
    out = {}
    for line in read:
        if ":" in line:  # Ignores Empty & Invalid lines
            spli = line.split(":", maxsplit=1)
            key = spli[0].strip()
            value = _get_value(spli[1])
            out[key] = value or []
        elif "-" in line:
            spli = line.split("-", maxsplit=1)
            if value := _get_value(spli[1]):
                where = out[list(out.keys())[-1]]
                if isinstance(where, list):
                    where.append(value)
    return out


def get_chat_and_msgid(link):
    matches = re.findall("https:\\/\\/t\\.me\\/(c\\/|)(.*)\\/(.*)", link)
    if not matches:
        return None, None
    _, chat, msg_id = matches[0]
    if chat.isdigit():
        chat = int("-100" + chat)
    return chat, int(msg_id)


# --------- END --------- #
