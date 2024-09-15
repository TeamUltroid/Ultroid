# Written by dot arc for Ultroid!
# rewritten by avish
"""
**Get Answers from Chat GPT (Open AI)**

> `{i}chatgpt` (-i = for image) (query)

**• Examples: **
> `{i}chatgpt How to fetch a url in javascript`
> `{i}chatgpt -i Cute Panda eating bamboo`

• First setup OpenAI Api key by using `.setdb OPENAI_API your_key` to use this plugin
"""
from io import BytesIO
from os import remove, system

try:
    from openai import OpenAI
except ImportError:
    system("pip install -q openai")
    from openai import OpenAI

from .. import LOGS, check_filename, fast_download, run_async, udB, ultroid_cmd


@run_async
def get_gpt_answer(gen_image, question, api_key):
    client = OpenAI(api_key=api_key)
    if gen_image:
        x = client.images.generate(prompt=question,
                                   model="dall-e-3",
                                   n=1,
                                   size="1792x1024",
                                   quality="hd",
                                   style="natural",
                                   user="arc")
        return x.data[0].url
    x = client.chat.completions.create(model=udB.get_key("OPENAI_MODEL") or "gpt-4o-mini",
                                       messages=[{"role": "user", "content": question}])
    LOGS.debug(f'Token Used on ({question}) > {x.usage.total_tokens}')
    return x.choices[0].message.content.lstrip("\n")


@ultroid_cmd(pattern="(chat)?chatgpt( (.*)|$)")
async def openai_chat_gpt(e):
    api_key = udB.get_key("OPENAI_API")
    gen_image = False
    if not api_key:
        return await e.eor("`OPENAI_API` key missing..")

    args = e.pattern_match.group(3)
    reply = await e.get_reply_message()
    if not args:
        if reply and reply.text:
            args = reply.message
    if not args:
        return await e.eor("`Gimme a Question to ask from ChatGPT`")

    moi = await e.eor(f"`getting response...`")
    if args.startswith("-i"):
        gen_image = True
        args = args[2:].strip()
    try:
        response = await get_gpt_answer(gen_image, args, api_key)
    except Exception as exc:
        LOGS.warning(exc, exc_info=True)
        return await moi.edit(f"**Error:** \n> `{exc}`")
    else:
        if gen_image:
            path, _ = await fast_download(
                response, filename=check_filename("dall-e.png")
            )
            await e.client.send_file(
                e.chat_id,
                path,
                caption=f"**{args[:1020]}**",
                reply_to=e.reply_to_msg_id,
            )
            await moi.delete()
            return remove(path)
        if len(response) < 4095:
            answer = f"<b>Query:</b>\n~ <i>{args}</i>\n\n<b>ChatGPT:</b>\n~ <i>{response}</i>"
            return await moi.edit(answer, parse_mode="html")
        with BytesIO(response.encode()) as file:
            file.name = "gpt_response.txt"
            await e.client.send_file(
                e.chat_id, file, caption=f"`{args[:1020]}`", reply_to=e.reply_to_msg_id
            )
        await moi.delete()
