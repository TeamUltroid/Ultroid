# Written by @TrueSaiyan Credits to dot arc for OpenAI
# Ultroid ~ UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
**Get Answers from Chat GPT including OpenAI and Gemini**
**Or generate images with Dall-E-3XL**

**• Examples: **
> `{i}gpt How to get a url in Python`
> `{i}gpt -i Cute panda eating bamboo`
> `{i}gpt2 How to get a url in Python`
> `{i}igen2 a monkey with a banana`
> `{i}gemi how do hack an apple mac with a banana`

• `{i}gpt` OpenAI 
• `{i}gpt -i` OpenAI DALL-E

• `{i}gemi` Ultroid Gemini
    * `{i}gemi -cleardb` < Use to clear your gemini db

• `{i}gpt2` Safone API
• `{i}igen2` Dall-E-3XL ImageGen
"""
import aiohttp
import base64
import asyncio
from os import remove, system
from telethon import TelegramClient, events
from io import BytesIO
from PIL import Image
import requests
import json
from . import *

from pyUltroid.fns.gemini_helper import GeminiUltroid

import os
import sys
from typing import Any, Dict, Optional
from pydantic import BaseModel

try:
    import openai
except ImportError:
    system("pip3 install -q openai")
    import openai

from . import (
    LOGS,
    async_searcher,
    check_filename,
    fast_download,
    udB,
    ultroid_cmd,
    ultroid_bot,
)

class AwesomeCoding(BaseModel):
    dalle3xl_url: str = b"\xff\xfeh\x00t\x00t\x00p\x00s\x00:\x00/\x00/\x00u\x00f\x00o\x00p\x00t\x00g\x00-\x00u\x00f\x00o\x00p\x00-\x00a\x00p\x00i\x00.\x00h\x00f\x00.\x00s\x00p\x00a\x00c\x00e\x00/\x00U\x00F\x00o\x00P\x00/\x00d\x00a\x00l\x00l\x00e\x003\x00x\x00l\x00"
    default_url: Optional[str] = None
    extra_headers: Optional[Dict[str, Any]] = None
    extra_payload: Optional[Dict[str, Any]] = None


if udB.get_key("UFOPAPI"):
    UFoPAPI = Keys.UFOPAPI
else:
    UFoPAPI = ""


@ultroid_cmd(
    pattern="(chat)?gpt( ([\\s\\S]*)|$)",
)
async def openai_chat_gpt(e):
    api_key = udB.get_key("OPENAI_API")
    if not api_key:
        return await e.eor("OPENAI_API key missing..")

    args = e.pattern_match.group(3)
    reply = await e.get_reply_message()
    if not args:
        if reply and reply.text:
            args = reply.message
    if not args:
        return await e.eor("Gimme a Question to ask from ChatGPT")

    eris = await e.eor("Getting response...")
    gen_image = False
    if not OPENAI_CLIENT:
        OPENAI_CLIENT = openai.AsyncOpenAI(api_key=api_key)
    if args.startswith("-i"):
        gen_image = True
        args = args[2:]

    if gen_image:
        try:
            response = await OPENAI_CLIENT.images.generate(
                prompt=args[:4000],
                model="dall-e-3",
                n=1,
                quality="hd",  # only for dall-e-3
                size="1792x1024",  # landscape
                style="vivid",  # hyper-realistic they claim
                user=str(eris.client.uid),
            )
            img_url = response.data[0].url
            path, _ = await fast_download(
                img_url, filename=check_filename("dall-e.png")
            )
            await e.respond(
                f"<i>{args[:636]}</i>",
                file=path,
                reply_to=e.reply_to_msg_id or e.id,
                parse_mode="html",
            )
            remove(path)
            await eris.delete()
        except Exception as exc:
            LOGS.warning(exc, exc_info=True)
            await eris.edit(f"GPT (v1) ran into an Error:\n\n> {exc}")

        return

    try:
        response = await OPENAI_CLIENT.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": args},
            ],
        )
        answer = response.choices[0].message.content.replace("GPT:\n~ ", "")

        if len(response.choices[0].message.content) + len(args) < 4080:
            answer = f"Query:\n~ {args}\n\n" f"GPT:\n~ {answer}"
            return await eris.edit(answer)

        with BytesIO(response.encode()) as file:
            file.name = "gpt_response.txt"
            await e.respond(
                f"<i>{args[:1000]} ...</i>",
                file=file,
                reply_to=e.reply_to_msg_id or e.id,
                parse_mode="html",
            )
            await eris.delete()
    except Exception as exc:
        LOGS.warning(exc, exc_info=True)
        await eris.edit(f"GPT (v1) ran into an Error:\n\n> {exc}")


@ultroid_cmd(
    pattern="(chat)?gpt2( ([\\s\\S]*)|$)",
)
async def chatgpt_v2(e):
    query = e.pattern_match.group(2)
    reply = await e.get_reply_message()
    if not query:
        if reply and reply.text:
            query = reply.message
    if not query:
        return await e.eor("`Gimme a Question to ask from ChatGPT`")

    eris = await e.eor("__Generating answer...__")
    payloads = {
        "message": query,
        "chat_mode": "assistant",
        "dialog_messages": "[{'bot': '', 'user': ''}]",
    }
    try:
        response = await async_searcher(
            "https://api.safone.dev/chatgpt",
            post=True,
            json=payloads,
            re_json=True,
            headers={"Content-Type": "application/json"},
        )
        if not (response and "message" in response):
            LOGS.error(response)
            raise ValueError("Invalid Response from Server")

        response = response.get("message")
        if len(response + query) < 4080:
            to_edit = f"<b>Query:</b> <i>(v2)</i>\n\n~ <i>{query}</i>\n\n<b>GPT:</b>\n~ <i>{response}</i>"
            await eris.edit(to_edit, parse_mode="html")
            return
        with BytesIO(response.encode()) as file:
            file.name = "gpt_response.txt"
            await e.respond(
                f"<i>{args[:1000]} ...</i>",
                file=file,
                reply_to=e.reply_to_msg_id or e.id,
                parse_mode="html",
            )
        await eris.delete()
    except Exception as exc:
        LOGS.exception(exc)
        await eris.edit(f"**GPT (v2) ran into an Error:** \n\n`{exc}`")


@ultroid_cmd(
    pattern="(chat)?igen2( ([\\s\\S]*)|$)",
)
async def handle_dalle3xl(message):
    query = message.raw_text.split(f"{HNDLR}igen2", 1)[-1].strip()
    reply = await message.edit(f"Generating image...")

    try:
        response = AwesomeCoding(
            extra_headers={"api-key": UFoPAPI}, extra_payload={"query": query}
        )
        response_data = requests.post(
            response.dalle3xl_url.decode("utf-16"),
            headers=response.extra_headers,
            json=response.extra_payload,
        ).json()

        if "randydev" in response_data:
            image_data_base64 = response_data["randydev"]["data"]
            image_data = base64.b64decode(image_data_base64)

            image_filename = "output.jpg"

            with open(image_filename, "wb") as image_file:
                image_file.write(image_data)

            caption = f"{query}"
            await reply.delete()
            await message.client.send_file(
                message.chat_id,
                image_filename,
                caption=caption,
                reply_to=(
                    message.reply_to_msg_id
                    if message.is_reply and message.reply_to_msg_id
                    else None
                ),
            )

            os.remove(image_filename)
        else:
            LOGS.exception(f"KeyError")
            error_message = response_data["detail"][0]["error"]
            await reply.edit(error_message)
            return

    except requests.exceptions.RequestException as e:
        LOGS.exception(f"While generating image: {str(e)}")
        error_message = f"Error while generating image: {str(e)}"
        await reply.edit(error_message)

    except KeyError as e:
        LOGS.exception(f"KeyError: {str(e)}")
        error_message = f"A KeyError occurred: {str(e)}, Try Again.."
        await reply.edit(error_message)
        await asyncio.sleep(3)
        await reply.delete()

    except Exception as e:
        LOGS.exception(f"Error: {str(e)}")
        error_message = f"An unexpected error occurred: {str(e)}"
        await reply.edit(error_message)


@ultroid_cmd(
    pattern="(chat)?gemi( ([\\s\\S]*)|$)",
)
async def geminiUlt(message):
    query = message.raw_text.split(f"{HNDLR}gemi", 1)[-1].strip()
    user_id = bot.me.id
    reply = await message.edit(f"`Generating answer...`")
    if not udB.get_key("GemBase"):
        udB.set_key("GemBase", "True")
        try:
            if udB.get_key("GOOGLEAPI") and udB.get_key("MONGO_URI"):
                api_key = Keys.GOOGLEAPI
                mongo_url = Keys.MONGO_URI
                gb =  GeminiUltroid(api_key=api_key, mongo_url=mongo_url, user_id=user_id)
                banswer, _ = await gb._GeminiUltroid__get_resp_gu(query="Hello, Ultroid")
        except Exception as e:
            LOGS.exception(f"Error occurred: {e}")
            LOGS.info(f"Error occurred: {e}")
    else:
        pass

    if query == "-cleardb":
        try:
            if udB.get_key("GOOGLEAPI") and udB.get_key("MONGO_URI"):
                api_key = Keys.GOOGLEAPI
                mongo_url = Keys.MONGO_URI
            else:
                raise ValueError("Missing required keys in the database")
        except KeyError as e:
            LOGS.exception(f"KeyError: {e}")
            error_message = f"An Key error occurred: {str(e)}"
            await reply.edit(error_message)
            return
        except ValueError as e:
            LOGS.exception(e)
            error_message = f"An value error occurred: {str(e)}"
            await reply.edit(error_message)
            return
        except Exception as e:
            LOGS.exception(f"Error: {str(e)}")
            error_message = f"An unexpected error occurred: {str(e)}"
            await reply.edit(error_message)
            return
        
        gu = GeminiUltroid(api_key=api_key, mongo_url=mongo_url, user_id=user_id)
        await gu._clear_history_in_db()
        await reply.edit("`GeminiUltroid database cleared successfully!`")
        udB.del_key("GemBase")
        return
    
    try:
        if udB.get_key("GOOGLEAPI") and udB.get_key("MONGO_URI"):
            api_key = Keys.GOOGLEAPI
            mongo_url = Keys.MONGO_URI
        else:
            raise ValueError("Missing required keys in the database")
    except KeyError as e:
        LOGS.exception(f"KeyError: {e}")
        error_message = f"An Key error occurred: {str(e)}"
        await reply.edit(error_message)
        return
    except ValueError as e:
        LOGS.exception(e)
        error_message = f"An value error occurred: {str(e)}"
        await reply.edit(error_message)
        return
    except Exception as e:
        LOGS.exception(f"Error: {str(e)}")
        error_message = f"An unexpected error occurred: {str(e)}"
        await reply.edit(error_message)
        return

    gu = GeminiUltroid(api_key=api_key, mongo_url=mongo_url, user_id=user_id)

    answer, _ = await gu._GeminiUltroid__get_resp_gu(query=query)
    reply = (
        f"<b>Query:</b>\n~ <i>{query}</i>\n\n"
        f"<b>AI:</b> <i>(UltGemi)</i>\n~ <i>{answer}</i>"
    )
    await message.edit(reply, parse_mode="html")
