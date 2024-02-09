# Written by @TrueSaiyan Credits to dot arc for OpenAI
# Ultroid ~ UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
**Get Answers from Chat GPT including OpenAI, Bing and Sydney**
**Or generate images with Dall-E-3XL**

> `{i}gpt` (-i = for image) (query)

**• Examples: **
> `{i}gpt How to fetch a url in javascript`
> `{i}gpt -i Cute Panda eating bamboo`
> `{i}gpt2 How to get a url in Python`
> `{i}bard Hello world`

• `{i}gpt` or `{i}gpt -i` Needs OpenAI API key to function!!
• `{i}gpt2` Safone API
• `{i}bard` Need to save bard cookie to use bard. (Its still learning)
"""
import aiohttp
import asyncio
from os import remove, system
from telethon import TelegramClient, events
from io import BytesIO
from PIL import Image
import base64
import requests
import json
from . import *


try:
    import openai
    from bardapi import Bard
except ImportError:
    system("pip3 install -q openai")
    system("pip3 install -q bardapi")
    import openai
    from bardapi import Bard

from . import (
    LOGS,
    async_searcher,
    check_filename,
    fast_download,
    udB,
    ultroid_cmd,
)

if udB.get_key("UFOPAPI"):
    UFoPAPI = udB.get_key("UFOPAPI")
else:
    UFoPAPI = ""

if udB.get_key("BARDAPI"):
    BARD_TOKEN = udB.get_key("BARDAPI")
else:
    BARD_TOKEN = None
    

#------------------------------ GPT v1 ------------------------------#
# OpenAI API-Key Required                                            |
#--------------------------------------------------------------------#
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
            path, _ = await fast_download(img_url, filename=check_filename("dall-e.png"))
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
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": args}],
        )
        # LOGS.debug(f'Token Used on ({question}) > {response["usage"]["total_tokens"]}')
        answer = response.choices[0].message.content.replace("GPT:\n~ ", "")

        if len(response.choices[0].message.content) + len(args) < 4080:
            answer = (
                f"Query:\n~ {args}\n\n"
                f"GPT:\n~ {answer}"
            )
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


#--------------------------Bard w Base ----------------------------#
# Bard Cookie Token.                                               |
#------------------------------------------------------------------#

@ultroid_cmd(
    pattern="(chat)?bard( ([\\s\\S]*)|$)",
)
async def handle_bard(message):
    owner_base = "You are an AI Assistant chatbot called Ultroid AI designed for many different helpful purposes"
    query = message.raw_text.split('.bard', 1)[-1].strip()
    reply = await message.edit(f"Generating answer...")

    if BARD_TOKEN:
        token = BARD_TOKEN
    else:
        error_message = f"ERROR NO BARD COOKIE TOKEN"
        await reply.edit(error_message)
        return

    try:
        headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
        }

        cookies = {"__Secure-1PSID": token}

        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            bard = Bard(token=token, session=session, timeout=30)
            bard.get_answer(owner_base)["content"]
            message_content = bard.get_answer(query)["content"]
            await reply.edit(message_content)

    except Exception as e:
        LOGS.exception(f"Error: {str(e)}")
        error_message = f"An unexpected error occurred: {str(e)}"
        await reply.edit(error_message)


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

