# credits - dot arc

"""
**Get Answers from Chat GPT (Open AI)**

> `{i}gpt` (-i = for image) (query)

**• Examples: **
> `{i}gpt How to fetch a url in javascript`
> `{i}gpt -i Cute Panda eating bamboo` 

☠️ It needs OpenAI api key to function! ☠️
"""

import asyncio
import os
import openai

from .. import ultroid_cmd, check_filename, udB, LOGS, fast_download


def get_gpt_answer(gen_image, question, api_key):
    openai.api_key = api_key
    if gen_image:
        x = openai.Image.create(
            prompt=question,
            n=1,
            size="1024x1024",
            user="arc",
        )
        return x["data"][0]["url"]
    x = openai.Completion.create(
        model=udB.get_key("GPT_MODEL") or "text-davinci-003",
        prompt=question,
        temperature=0.5,
        stop=None,
        n=1,
        user="arc",
        max_tokens=768,
    )
    LOGS.debug(f'Token Used on ({question}) > {x["usage"]["total_tokens"]}')
    return x["choices"][0].text.strip()


@ultroid_cmd(pattern="gpt ?(.*)")
async def openai_chat_gpt(e):
    api_key = udB.get_key("OPENAI_API")
    gen_image = False
    if not api_key:
        return await e.eor("`OPENAI_API` key missing..")

    args = e.pattern_match.group(1)
    reply = await e.get_reply_message()
    if not args:
        if reply and reply.text:
            args = reply.message
    if not args:
        return await e.eor("`Gimme a Question to ask from ChatGPT`")

    if args.startswith("-i"):
        gen_image = True
        args = args[2:].strip()
        edit_text = "image"
    else:
        edit_text = "answer"

    m = await e.eor(f"`getting {edit_text} from chatgpt..`")
    response = await asyncio.to_thread(get_gpt_answer, gen_image, args, api_key)
    if response:
        if not gen_image:
            await m.edit(
                f"**Query :** \n~ __{args}__ \n\n**ChatGPT :** \n~ __{response}__"
            )
            return
        path, _ = await fast_download(response, filename=check_filename("dall-e.png"))
        await e.eor(f"<b>{args[:1023]}</b>", file=path, parse_mode="html")
        os.remove(path)
        await m.delete()