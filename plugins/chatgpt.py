# Written by @TrueSaiyan Credits to dot arc for OpenAI
# Ultroid ~ UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
**Get Answers from Chat GPT including OpenAI, Bing or Sydney**

> `{i}gpt` (-i = for image) (query)

**• Examples: **
> `{i}gpt How to fetch a url in javascript`
> `{i}gpt -i Cute Panda eating bamboo`
> `{i}gpt3t write me an essay`
> `{i}gpt4 Tell me a joke` `can you tell me another`
> `{i}igen Cute Panda eating bamboo`

• `{i}gpt` or `{i}gpt -i` Needs OpenAI API key to function!!
• `{i}gpt3t` OpenAI GPT35-Turbo
• `{i}bing` Bing/Sydney/CoPilot AI w History
• `{i}igen` Dall-E-3-XL
"""
import asyncio
from os import remove, system
from telethon import TelegramClient, events
from io import BytesIO
from PIL import Image
import base64
import requests
import json
from pyUltroid.fns.tools import AwesomeCoding
from . import *


try:
    import openai
except ImportError:
    system("pip3 install -q openai==0.28.0")
    import openai

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
 
if not udB.get_key("GPTbase"):
    udB.set_key("GPTbase", "https://gpt-api.mycloud.im/v1")
    

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


#----------------------------- GPT v3.5 -----------------------------#
# No API-Key Required      .setdb GPTbase        openai==0.28.0      |
#--------------------------------------------------------------------#

gpt35_conversation_history = []

@ultroid_cmd(
    pattern="(chat)?gpt3t( ([\\s\\S]*)|$)",
)
async def handle_gpt35(message):
    openai.api_key = "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"
    openai.api_base = udB.get_key("GPTbase")
    global gpt35_conversation_history

    query = message.raw_text.split(',gpt3t', 1)[-1].strip()
    reply = await message.edit(f"`Generating answer...`")

    gpt35_conversation_history.append({"role": "user", "content": query})

    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-long",
        messages=gpt35_conversation_history,
        stream=True,
    )

    if isinstance(chat_completion, dict):
        answer = chat_completion.choices[0].message.content
    else:
        answer = ""
        for token in chat_completion:
            content = token["choices"][0]["delta"].get("content")
            if content is not None:
                answer += content

    gpt35_conversation_history.append({"role": "assistant", "content": answer})

    reply = (
        f"<b>Query:</b>\n~ <i>{query}</i>\n\n"
        f"<b>GPT:</b> <i>(OpenAI GPT-3.5)</i>\n~ <i>{answer}</i>"
    )
    await message.edit(reply, parse_mode="html")

#----------------------------- GPT v4 -----------------------------#
# No API-Key Required      .setdb GPTbase        openai==0.28.0    |
#------------------------------------------------------------------#

bing_conversation_history = []

@ultroid_cmd(
    pattern="(chat)?bing( ([\\s\\S]*)|$)",
)
async def handle_gpt4(message):
    openai.api_key = "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"
    openai.api_base = udB.get_key("GPTbase")
    global bing_conversation_history

    query = message.raw_text.split('.bing', 1)[-1].strip()
    reply = await message.edit(f"Generating answer...")

    bing_conversation_history.append({"role": "user", "content": query})

    chat_completion = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=bing_conversation_history,
        stream=True,
    )

    if isinstance(chat_completion, dict):
        answer = chat_completion.choices[0].message.content
    else:
        answer = ""
        for token in chat_completion:
            content = token["choices"][0]["delta"].get("content")
            if content is not None:
                answer += content

    bing_conversation_history.append({"role": "assistant", "content": answer})

    reply = (
        f"<b>Query:</b>\n~ <i>{query}</i>\n\n"
        f"<b>GPT:</b> <i>(Bing/Sydney/Copilot)</i>\n~ <i>{answer}</i>"
    )
    await message.edit(reply, parse_mode="html")

#----------------------------- Dall-E -----------------------------#
# No API-Key Required                                              |
#------------------------------------------------------------------#

@ultroid_cmd(
    pattern="(chat)?igen( ([\\s\\S]*)|$)",
)
async def handle_dalle3xl(message):
    query = message.raw_text.split(',igen', 1)[-1].strip()
    reply = await message.edit(f"Generating image...")

    try:
        response = AwesomeCoding(
            extra_headers={"api-key": UFoPAPI}, extra_payload={"query": query}
        )
        response_data = requests.post(
            response.dalle3xl_url.decode("utf-16"),
            headers=response.extra_headers,
            json=response.extra_payload).json()

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
                reply_to=message.reply_to_msg_id if message.is_reply and message.reply_to_msg_id else None,
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
