import openai

from .. import udB, ultroid_cmd

openai.api_key = udB.get("OPENAI_KEY")


@ultroid_cmd(pattern="chatgpt( (.*)|$)")
async def chatgpt(event):
    """Chat with GPT-3"""
    if not udB.get("OPENAI_KEY"):
        return await event.eor("Set `OPENAI_API_KEY` in Heroku Config Vars")
    query = event.pattern_match.group(1).strip()
    reply_message = await event.get_reply_message()
    if not query and (reply_message and reply_message.text):
        query = reply_message.text
    if not query:
        return await event.eor("Reply to a message to chat with GPT-3")
    message = await event.eor("Chatting with GPT-3...")
    output = openai.Completion.create(
        engine=udB.get_key("GPT_MODEL") or "davinci",
        prompt=query,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["\n", " User:", " AI:"],
    )
    await message.edit(f"__{query}__: \n__{output['choices'][0]['text']}__")
