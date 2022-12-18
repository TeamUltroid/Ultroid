# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

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

from .. import *
from ..exceptions import DependencyMissingError
from .helper import bash, run_async

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

try:
    import requests
    from requests.exceptions import MissingSchema
except ImportError:
    requests = None
from telethon import Button
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo

if run_as_module:
    from ..dB.filestore_db import get_stored_msg, store_msg

try:
    import numpy as np
except ImportError:
    np = None

try:
    from telegraph import Telegraph
except ImportError:
    Telegraph = None

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


# ~~~~~~~~~~~~~~~Async Searcher~~~~~~~~~~~~~~~
# @buddhhu


async def async_searcher(
    url: str,
    post: bool = None,
    headers: dict = None,
    params: dict = None,
    json: dict = None,
    data: dict = None,
    ssl=None,
    re_json: bool = False,
    re_content: bool = False,
    real: bool = False,
    *args,
    **kwargs,
):
    try:
        import aiohttp
    except ImportError:
        raise DependencyMissingError(
            "'aiohttp' is not installed!\nthis function requires aiohttp to be installed."
        )
    async with aiohttp.ClientSession(headers=headers) as client:
        if post:
            data = await client.post(
                url, json=json, data=data, ssl=ssl, *args, **kwargs
            )
        else:
            data = await client.get(url, params=params, ssl=ssl, *args, **kwargs)
        if re_json:
            return await data.json()
        if re_content:
            return await data.read()
        if real:
            return data
        return await data.text()


# ~~~~~~~~~~~~~~~JSON Parser~~~~~~~~~~~~~~~
# @buddhhu


def _unquote_text(text):
    return text.replace("'", unquote("%5C%27")).replace('"', unquote("%5C%22"))


def json_parser(data, indent=None, ascii=False):
    parsed = {}
    try:
        if isinstance(data, str):
            parsed = json.loads(str(data))
            if indent:
                parsed = json.dumps(
                    json.loads(str(data)), indent=indent, ensure_ascii=ascii
                )
        elif isinstance(data, dict):
            parsed = data
            if indent:
                parsed = json.dumps(data, indent=indent, ensure_ascii=ascii)
    except JSONDecodeError:
        parsed = eval(data)
    return parsed


# ~~~~~~~~~~~~~~~~Link Checker~~~~~~~~~~~~~~~~~


def is_url_ok(url: str):
    try:
        import requests
    except ImportError:
        raise DependencyMissingError("This function needs 'requests' to be installed.")
    try:
        r = requests.head(url)
    except MissingSchema:
        return None
    except BaseException:
        return False
    return r.ok


# ~~~~~~~~~~~~~~~~ Metadata ~~~~~~~~~~~~~~~~~~~~


async def metadata(file):
    out, _ = await bash(f'mediainfo "{_unquote_text(file)}" --Output=JSON')
    if _ and _.endswith("NOT_FOUND"):
        raise Exception(_)
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


def get_all_files(path, extension=None):
    filelist = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if not (extension and not file.endswith(extension)):
                filelist.append(os.path.join(root, file))
    return sorted(filelist)


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


# ------------------Logo Gen Helpers----------------
# @TechiError


class LogoHelper:
    @staticmethod
    def get_text_size(text, image, font):
        im = Image.new("RGB", (image.width, image.height))
        draw = ImageDraw.Draw(im)
        return draw.textsize(text, font)

    @staticmethod
    def find_font_size(text, font, image, target_width_ratio):
        tested_font_size = 100
        tested_font = ImageFont.truetype(font, tested_font_size)
        observed_width, observed_height = LogoHelper.get_text_size(
            text, image, tested_font
        )
        estimated_font_size = (
            tested_font_size / (observed_width / image.width) * target_width_ratio
        )
        return round(estimated_font_size)

    @staticmethod
    def make_logo(imgpath, text, funt, **args):
        fill = args.get("fill")
        width_ratio = args.get("width_ratio") or 0.7
        stroke_width = int(args.get("stroke_width"))
        stroke_fill = args.get("stroke_fill")

        img = Image.open(imgpath)
        width, height = img.size
        draw = ImageDraw.Draw(img)
        font_size = LogoHelper.find_font_size(text, funt, img, width_ratio)
        font = ImageFont.truetype(funt, font_size)
        w, h = draw.textsize(text, font=font)
        draw.text(
            ((width - w) / 2, (height - h) / 2),
            text,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        file_name = check_filename("logo.png")
        img.save(file_name, "PNG")
        return file_name


# --------------------------------------
# @New-Dev0


async def get_paste(data: str, extension: str = "txt"):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    json = {"content": data, "extension": extension}
    key = await async_searcher(
        url="https://spaceb.in/api/v1/documents/",
        json=json,
        ssl=ssl_context,
        post=True,
        re_json=True,
    )
    try:
        return True, key["payload"]["id"]
    except KeyError:
        if "the length must be between 2 and 400000." in key["error"]:
            return await get_paste(data[-400000:], extension=extension)
        return False, key["error"]
    except Exception as e:
        LOGS.info(e)
        return None, str(e)


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
        minutes = "0" + str(minutes)
    if len(str(hours)) == 1:
        hours = "0" + str(hours)
    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)
    return (
        ((str(hours) + ":") if hours else "00:")
        + ((str(minutes) + ":") if minutes else "00:")
        + ((str(seconds)) if seconds else "")
    )


# ------------------- used in pdftools --------------------#

# https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example


def order_points(pts):
    "get the required points"
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
        raise DependencyMissingError("This function needs 'cv2' to be installed.")
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


# ------------------------------------- Telegraph ---------------------------------- #
TELEGRAPH = []


def telegraph_client():
    if not Telegraph:
        LOGS.info("'Telegraph' is not Installed!")
        return
    if TELEGRAPH:
        return TELEGRAPH[0]

    from .. import udB, ultroid_bot

    token = udB.get_key("_TELEGRAPH_TOKEN")
    TelegraphClient = Telegraph(token)
    if token:
        TELEGRAPH.append(TelegraphClient)
        return TelegraphClient
    gd_name = ultroid_bot.full_name
    short_name = gd_name[:30]
    profile_url = (
        f"https://t.me/{ultroid_bot.me.username}"
        if ultroid_bot.me.username
        else "https://t.me/TeamUltroid"
    )
    try:
        TelegraphClient.create_account(
            short_name=short_name, author_name=gd_name, author_url=profile_url
        )
    except Exception as er:
        if "SHORT_NAME_TOO_LONG" in str(er):
            TelegraphClient.create_account(
                short_name="ultroiduser", author_name=gd_name, author_url=profile_url
            )
        else:
            LOGS.exception(er)
            return
    udB.set_key("_TELEGRAPH_TOKEN", TelegraphClient.get_access_token())
    TELEGRAPH.append(TelegraphClient)
    return TelegraphClient


@run_async
def make_html_telegraph(title, html=""):
    telegraph = telegraph_client()
    page = telegraph.create_page(
        title=title,
        html_content=html,
    )
    return page["url"]


async def Carbon(
    code,
    base_url="https://rayso-api-desvhu-33.koyeb.app/generate",
    file_name="ultroid",
    download=False,
    rayso=False,
    **kwargs,
):
    # if rayso:
    kwargs["text"] = code
    kwargs["theme"] = kwargs.get("theme", "meadow")
    kwargs["darkMode"] = kwargs.get("darkMode", True)
    kwargs["title"] = kwargs.get("title", "Ultroid")
    # else:
    #    kwargs["code"] = code
    con = await async_searcher(base_url, post=True, json=kwargs, re_content=True)
    if not download:
        file = BytesIO(con)
        file.name = file_name + ".jpg"
    else:
        file = file_name + ".jpg"
        with open(file, "wb") as f:
            f.write(con)
    return file


async def get_file_link(msg):
    from .. import udB

    msg_id = await msg.forward_to(udB.get_key("LOG_CHANNEL"))
    await msg_id.reply(
        "**Message has been stored to generate a shareable link. Do not delete it.**"
    )
    msg_id = msg_id.id
    msg_hash = secrets.token_hex(nbytes=8)
    store_msg(msg_hash, msg_id)
    return msg_hash


async def get_stored_file(event, hash):
    from .. import udB

    msg_id = get_stored_msg(hash)
    if not msg_id:
        return
    try:
        msg = await asst.get_messages(udB.get_key("LOG_CHANNEL"), ids=msg_id)
    except Exception as er:
        LOGS.warning(f"FileStore, Error: {er}")
        return
    if not msg_id:
        return await asst.send_message(
            event.chat_id, "__Message was deleted by owner!__", reply_to=event.id
        )
    await asst.send_message(event.chat_id, msg.text, file=msg.media, reply_to=event.id)


def _package_rpc(text, lang_src="auto", lang_tgt="auto"):
    GOOGLE_TTS_RPC = ["MkEWBc"]
    parameter = [[text.strip(), lang_src, lang_tgt, True], [1]]
    escaped_parameter = json.dumps(parameter, separators=(",", ":"))
    rpc = [[[random.choice(GOOGLE_TTS_RPC), escaped_parameter, None, "generic"]]]
    espaced_rpc = json.dumps(rpc, separators=(",", ":"))
    freq = "f.req={}&".format(quote(espaced_rpc))
    return freq


def translate(*args, **kwargs):
    headers = {
        "Referer": "https://translate.google.co.in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/47.0.2526.106 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    x = requests.post(
        "https://translate.google.co.in/_/TranslateWebserverUi/data/batchexecute",
        headers=headers,
        data=_package_rpc(*args, **kwargs),
    ).text
    response = ""
    data = json.loads(json.loads(x[4:])[0][2])[1][0][0]
    subind = data[-2]
    if not subind:
        subind = data[-1]
    for i in subind:
        response += i[0]
    return response


def cmd_regex_replace(cmd):
    return (
        cmd.replace("$", "")
        .replace("?(.*)", "")
        .replace("(.*)", "")
        .replace("(?: |)", "")
        .replace("| ", "")
        .replace("( |)", "")
        .replace("?((.|//)*)", "")
        .replace("?P<shortname>\\w+", "")
        .replace("(", "")
        .replace(")", "")
        .replace("?(\\d+)", "")
    )


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
    def resize_photo_sticker(photo):
        """Resize the given photo to 512x512 (for creating telegram sticker)."""
        image = Image.open(photo)
        if (image.width and image.height) < 512:
            size1 = image.width
            size2 = image.height
            if image.width > image.height:
                scale = 512 / size1
                size1new = 512
                size2new = size2 * scale
            else:
                scale = 512 / size2
                size1new = size1 * scale
                size2new = 512
            size1new = math.floor(size1new)
            size2new = math.floor(size2new)
            sizenew = (size1new, size2new)
            image = image.resize(sizenew)
        else:
            maxsize = (512, 512)
            image.thumbnail(maxsize)
        return image

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
            raise DependencyMissingError("This function needs 'cv2' to be installed.")
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
    try:
        value = eval(stri.strip())
    except Exception as er:
        from .. import LOGS

        LOGS.debug(er)
        value = stri.strip()
    return value


def safe_load(file, *args, **kwargs):
    if isinstance(file, str):
        read = file.split("\n")
    else:
        read = file.readlines()
    out = {}
    for line in read:
        if ":" in line:  # Ignores Empty & Invalid lines
            spli = line.split(":", maxsplit=1)
            key = spli[0].strip()
            value = _get_value(spli[1])
            out.update({key: value or []})
        elif "-" in line:
            spli = line.split("-", maxsplit=1)
            where = out[list(out.keys())[-1]]
            if isinstance(where, list):
                value = _get_value(spli[1])
                if value:
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
