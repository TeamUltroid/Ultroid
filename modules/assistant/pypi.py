# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
from . import *
import hashlib
import inspect
import os
import re
from datetime import datetime
from html import unescape
from random import choice
from re import compile as re_compile
from bs4 import BeautifulSoup as bs

try:
    from markdownify import markdownify as md
except ImportError:
    system("pip3 install -q markdownify")

from telethon import Button
from telethon.tl.alltlobjects import LAYER, tlobjects
from telethon.tl.types import DocumentAttributeAudio as Audio
from telethon.tl.types import InputWebDocument as wb
from telethon.tl.types import MessageEntityTextUrl

hash_to_url = {}


def generate_unique_id(url):
    hashed_id = hashlib.sha256(url.encode()).hexdigest()[:8]
    hash_to_url[hashed_id] = url
    return hashed_id


def get_original_url(hashed_id):
    return hash_to_url.get(hashed_id)


def clean_desc(description):
    # Remove lines starting with ".."
    description = re.sub(r"^\.\.", "", description, flags=re.MULTILINE)
    # Remove lines starting with "|"
    description = re.sub(r"^\|", "", description, flags=re.MULTILINE)
    # Remove lines starting with ":"
    description = re.sub(r"^:", "", description, flags=re.MULTILINE)
    # Remove lines starting with "  :"
    description = re.sub(r"^ {2}:", "", description, flags=re.MULTILINE)
    # Remove lines starting with "/3/"
    description = re.sub(r"/\d+/", "", description)
    # Remove lines starting with "code-block:: python"
    description = re.sub(
        r"^\s*code-block::.*$", "", description, flags=re.IGNORECASE | re.MULTILINE
    )
    # Remove any remaining leading or trailing whitespace
    description = description.strip()
    return description


PYPI_LIST = {}


@in_pattern("pypi")
async def inline_pypi_handler(event):
    pypimg = "https://graph.org/file/004c65a44efa1efc85193.jpg"
    BASE_URL = "https://pypi.org/pypi/{}/json"
    try:
        package = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await event.answer(
            [
                event.builder.article(
                    type="photo",
                    include_media=True,
                    title="sᴇᴀʀᴄʜ ᴘʏᴘɪ",
                    thumb=wb(pypimg, 0, "image/jpeg", []),
                    content=wb(pypimg, 0, "image/jpeg", []),
                    text=f"**ᴘʏᴘɪ sᴇᴀʀᴄʜ**\n\nʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴇᴀʀᴄʜ ғᴏʀ ᴀɴʏᴛʜɪɴɢ.",
                    buttons=[
                        Button.switch_inline(
                            "sᴇᴀʀᴄʜ ᴀɢᴀɪɴ",
                            query="pypi ",
                            same_peer=True,
                        ),
                    ],
                )
            ]
        )
        return

    response = await async_searcher(BASE_URL.format(package), re_json=True)
    if response is not None and "info" in response:
        info = response["info"]
        name = info["name"]
        url = info["package_url"]
        version = info["version"]
        summary = info["summary"]
        qid = generate_unique_id(name)
        txt = f"**ᴘᴀᴄᴋᴀɢᴇ:** [{name}]({url}) (`{version}`)\n\n**ᴅᴇᴛᴀɪʟs:** `{summary}`"

        offset = txt.find(name)
        length = len(name)
        url_entity = MessageEntityTextUrl(offset=offset, length=length, url=url)

        # Extract document links from description
        document_links = re.findall(r"(https?://\S+)", info["description"])

        buttons = [
            Button.inline("sʜᴏᴡ ᴅᴇᴛᴀɪʟs", data=f"pypi_details:{qid}"),
            Button.inline("ᴅᴏᴄᴜᴍᴇɴᴛ ʟɪɴᴋs", data=f"pypi_documents:{qid}"),
        ]

        await event.answer(
            [
                event.builder.article(
                    type="photo",
                    include_media=True,
                    title="ᴘᴀᴄᴋᴀɢᴇ ɪɴғᴏ",
                    thumb=wb(
                        "https://graph.org/file/f09380ada91534b2f6687.jpg",
                        0,
                        "image/jpeg",
                        [],
                    ),
                    content=wb(
                        "https://graph.org/file/f09380ada91534b2f6687.jpg",
                        0,
                        "image/jpeg",
                        [],
                    ),
                    description=f"{name}\n{version}",
                    text=txt,
                    buttons=buttons,
                )
            ]
        )

        PYPI_LIST.update(
            {
                qid: {
                    "info": info,
                    "name": name,
                    "url": url,
                    "version": version,
                    "summary": summary,
                    "text": txt,
                    "document_links": document_links,
                    "buttons": buttons,
                }
            }
        )
    else:
        await event.answer(
            [
                event.builder.article(
                    title="ᴘᴀᴄᴋᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ",
                    thumb=wb(pypimg, 0, "image/jpeg", []),
                    text=f"**ᴘᴀᴄᴋᴀɢᴇ:** `{package}`\n\n**ᴅᴇᴛᴀɪʟs:** `ɴᴏᴛ ғᴏᴜɴᴅ`",
                )
            ]
        )
    return


@callback(re.compile("pypi_details:(.*)"), owner=False)
async def show_details(event):
    qid = event.data.decode().split(":", 1)[1]
    if not PYPI_LIST.get(qid):
        return await event.answer("Qᴜᴇʀʏ ᴇxᴘɪʀᴇᴅ! Sᴇᴀʀᴄʜ ᴀɢᴀɪɴ 🔍")
    info = PYPI_LIST[qid]
    details = info["info"]

    author = details.get("author", "Uɴᴋɴᴏᴡɴ")
    author_email = details.get("author_email", "Uɴᴋɴᴏᴡɴ")
    classifiers = "\n".join(details.get("classifiers", []))
    description = details.get("description", "N/A")

    formatted_description = md(description)
    clean_description = re.sub(r"\*\*|`|\\|_", "", formatted_description)
    clean_description = clean_desc(clean_description)
    PYPI_LIST[qid]["description"] = clean_description

    text = f"**ᴀᴜᴛʜᴏʀ:** {author}\n"
    text += f"**ᴀᴜᴛʜᴏʀ ᴇᴍᴀɪʟ:** {author_email}\n"
    text += f"**ᴄʟᴀssɪғɪᴇʀs:**\n{classifiers}\n"

    if description == "N/A":
        buttons = [
            Button.inline("ʙᴀᴄᴋ", data=f"pypi_back_button:{qid}"),
        ]
        await event.edit(text, buttons=buttons)
    else:
        buttons = [
            Button.inline("ᴍᴏʀᴇ", data=f"pypi_description_more:{qid}"),
            Button.inline("ʙᴀᴄᴋ", data=f"pypi_back_button:{qid}"),
        ]
        await event.edit(text, buttons=buttons)


@callback(re.compile("pypi_documents:(.*)"), owner=True)
async def show_documents(event):
    qid = event.data.decode().split(":", 1)[1]
    if not PYPI_LIST.get(qid):
        return await event.answer("Qᴜᴇʀʏ ᴇxᴘɪʀᴇᴅ! Sᴇᴀʀᴄʜ ᴀɢᴀɪɴ 🔍")
    document_links = PYPI_LIST[qid]["document_links"]
    if document_links:
        text = "**ᴅᴏᴄ ʟɪɴᴋs**\n╭────────────────•\n"
        text += "\n".join(
            [
                f"╰➢ [{link.split('//')[1].split('/')[0]}]({link})"
                for link in document_links
            ]
        )
        text += "\n╰────────────────•"
        buttons = [
            Button.inline("ʙᴀᴄᴋ", data=f"pypi_back_button:{qid}"),
        ]
        await event.edit(text, buttons=buttons)
    else:
        await event.answer("ɴᴏ ᴅᴏᴄᴜᴍᴇɴᴛ ʟɪɴᴋs ғᴏᴜɴᴅ.")


@callback(re.compile("pypi_description_more:(.*)"), owner=True)
async def show_full_description(event):
    qid = event.data.decode().split(":", 1)[1]
    description = PYPI_LIST[qid].get("description")
    if description:
        already_defined_text_length = len("ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:\nPage X/Y\n")
        current_page = 1
        await show_description_with_pagination(
            event, qid, description, already_defined_text_length, current_page
        )


async def show_description_with_pagination(
    event, qid, description, already_defined_text_length, current_page
):
    available_length = 1024 - already_defined_text_length

    description_chunks = [
        description[i : i + available_length]
        for i in range(0, len(description), available_length)
    ]
    total_chunks = len(description_chunks)

    text = f"**ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:**\n**Pᴀɢᴇ** `{current_page}`/`{total_chunks}`\n{description_chunks[current_page - 1]}"
    buttons = [
        Button.inline("<<", data=f"pypi_description_page:{qid}:{current_page-1}"),
        Button.inline("ʙᴀᴄᴋ", data=f"pypi_back_button:{qid}"),
        Button.inline(">>", data=f"pypi_description_page:{qid}:{current_page+1}"),
    ]
    await event.edit(text, buttons=buttons)


@callback(re.compile("pypi_description_page:(.*):(\\d+)"), owner=True)
async def handle_description_page(event):
    qid, page = event.data.decode().split(":")[1:]
    description = PYPI_LIST[qid].get("description")
    if description:
        already_defined_text_length = len("ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:\nPage X/Y\n")
        page_number = int(page)
        await show_description_with_pagination(
            event,
            qid,
            description,
            already_defined_text_length,
            current_page=page_number,
        )


@callback(re.compile("pypi_back_button:(.*)"), owner=True)
async def back_button_clicked(event):
    qid = event.data.decode().split(":", 1)[1]
    if not PYPI_LIST.get(qid):
        return await event.answer("Qᴜᴇʀʏ ᴇxᴘɪʀᴇᴅ! Sᴇᴀʀᴄʜ ᴀɢᴀɪɴ 🔍")
    text = PYPI_LIST[qid]["text"]
    buttons = PYPI_LIST[qid]["buttons"]
    await event.edit(text, buttons=buttons)
