# credits - dot arc
# credits - @TrueSaiyan
#Plese note you mat need to make sure OpenAI 0.28.0 is installed or make sure that your version supports custom base 

"""
**Get Answers from Chat GPT including OpenAI, Bing, Google and Dall-E**

> `{i}gpt` (-i = for image) (query)

**• Examples: **
> `{i}gpt How to fetch a url in javascript`
> `{i}gpt -i Cute Panda eating bamboo`
> `{i}bing Tell me a joke` `can you tell me another`

• `{i}gpt` Needs OpenAI API key to function!!
• `{i}bing` Bing AI w History Powered by Alpha
"""

import asyncio
import os

import openai

from .. import LOGS, check_filename, fast_download, udB, ultroid_cmd


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


@ultroid_cmd(
    pattern="(chat)?bing( ([\\s\\S]*)|$)",
)
async def handle_gpt4(message):
    openai.api_key = udB.get_key("OPENAI_API") if udB.get_key("OPENAI_API") is not None else ""
    openai.api_base = udB.get_key("GPTbase") if udB.get_key("GPTbase") is not None else "https://gpt-api.mycloud.im/v1"
    global bing_conversation_history

    query = message.raw_text.split(".bing", 1)[-1].strip()
    reply = await message.edit(f"Generating answer...")

    # Append the user's query to the conversation history
    bing_conversation_history.append({"role": "user", "content": query})

    # Using OpenAI GPT-4 Turbo API with conversation history
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

    # Append the AI's response to the conversation history
    bing_conversation_history.append({"role": "assistant", "content": answer})

    reply = (
        f"<b>Query:</b>\n~ <i>{query}</i>\n\n"
        f"<b>GPT:</b> <i>(Bing Chat)</i>\n~ <i>{answer}</i>"
    )
    await message.edit(reply, parse_mode="html")
