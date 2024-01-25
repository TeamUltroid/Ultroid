# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# SOL UserBot #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# sqlalchemy
# openai
# fake_useragent
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Special Credits: @LucifSD02 <Telegram>
# Special Credits: @SoulOfSukuna <Telegram>
# Special Credits: @TrueSaiyan <Telegram>

import json
import os

import openai
import requests
from fake_useragent import UserAgent
from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont, ImageOps
from sqlalchemy import Column, String, UnicodeText

from addons.inlinegames import edit_delete, edit_or_reply, reply_id

from . import BASE, SESSION

openai.api_key = udB.get_key("OPENAI_API")  # OPENAI KEY

conversations = {}


class Globals(BASE):
    __tablename__ = "globals"
    variable = Column(String, primary_key=True, nullable=False)
    value = Column(UnicodeText, primary_key=True, nullable=False)

    def __init__(self, variable, value):
        self.variable = str(variable)
        self.value = value


Globals.__table__.create(checkfirst=True)


def gvarstatus(variable):
    try:
        return (
            SESSION.query(Globals)
            .filter(Globals.variable == str(variable))
            .first()
            .value
        )
    except BaseException:
        return None
    finally:
        SESSION.close()


def addgvar(variable, value):
    if SESSION.query(Globals).filter(Globals.variable == str(variable)).one_or_none():
        delgvar(variable)
    adder = Globals(str(variable), value)
    SESSION.add(adder)
    SESSION.commit()


def delgvar(variable):
    if rem := (
        SESSION.query(Globals)
        .filter(Globals.variable == str(variable))
        .delete(synchronize_session="fetch")
    ):
        SESSION.commit()


def format_image(filename):
    img = Image.open(filename).convert("RGBA")
    w, h = img.size
    if w != h:
        _min, _max = min(w, h), max(w, h)
        bg = img.crop(
            ((w - _min) // 2, (h - _min) // 2, (w + _min) // 2, (h + _min) // 2)
        )
        bg = bg.filter(ImageFilter.GaussianBlur(5))
        bg = bg.resize((_max, _max))
        img_new = Image.new("RGBA", (_max, _max), (255, 255, 255, 0))
        img_new.paste(
            bg, ((img_new.width - bg.width) // 2, (img_new.height - bg.height) // 2)
        )
        img_new.paste(img, ((img_new.width - w) // 2, (img_new.height - h) // 2))
        img = img_new
    img.save(filename)


async def wall_download(piclink, query, ext=".jpg"):
    try:
        if not os.path.isdir("./temp"):
            os.mkdir("./temp")
        picpath = f"./temp/{query.title().replace(' ', '')}{ext}"
        if os.path.exists(picpath):
            i = 1
            while os.path.exists(picpath) and i < 11:
                picpath = f"./temp/{query.title().replace(' ', '')}-{i}{ext}"
                i += 1
        with open(picpath, "wb") as f:
            f.write(requests.get(piclink).content)
        return picpath
    except Exception as e:
        LOGS.info(str(e))
        return None


def generate_gpt_response(input_text, chat_id):
    global conversations
    model = gvarstatus("CHAT_MODEL") or "gpt-3.5-turbo"
    system_message = gvarstatus("SYSTEM_MESSAGE") or None
    messages = conversations.get(chat_id, [])

    # Add system message if it exists
    if system_message and not messages:
        messages.append({"role": "system", "content": system_message})

    # Add the new user message
    messages.append({"role": "user", "content": input_text})
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )
        generated_text = response.choices[0].message.content.strip()

        # Save the assistant's response to the conversation history
        messages.append({"role": "assistant", "content": generated_text})
        conversations[chat_id] = messages
    except Exception as e:
        generated_text = f"`Error generating GPT response: {str(e)}`"
    return generated_text


def generate_edited_response(input_text, instructions):
    try:
        response = openai.Edit.create(
            model="text-davinci-edit-001",
            input=input_text,
            instruction=instructions,
        )
        edited_text = response.choices[0].text.strip()
    except Exception as e:
        edited_text = f"__Error generating GPT edited response:__ `{str(e)}`"
    return edited_text


def del_convo(chat_id, checker=False):
    global conversations
    out_text = "__There is no GPT context to delete for this chat.__"
    # Delete the the context of given chat
    if chat_id in conversations:
        del conversations[chat_id]
        out_text = "__GPT context deleted for this chat.__"
    if checker:
        return out_text


async def generate_dalle_image(text, reply, event, flag=None):
    size = gvarstatus("DALLE_SIZE") or "1024"
    limit = int(gvarstatus("DALLE_LIMIT") or "1")
    if not text and reply:
        text = reply.text
    if not text:
        return await edit_delete(event, "**ಠ∀ಠ Gimmi text**")

    catevent = await edit_or_reply(event, "__Generating image...__")
    try:
        if flag:
            filename = "dalle-in.png"
            await event.client.download_media(reply, filename)
            format_image(filename)
            if flag == "e":
                response = openai.Image.create_edit(
                    image=open(filename, "rb"),
                    prompt=text,
                    n=limit,
                    size=f"{size}x{size}",
                )
            elif flag == "v":
                response = openai.Image.create_variation(
                    image=open(filename, "rb"),
                    n=limit,
                    size=f"{size}x{size}",
                )
            os.remove(filename)
        else:
            response = openai.Image.create(
                prompt=text,
                n=limit,
                size=f"{size}x{size}",
            )
    except Exception as e:
        await edit_delete(catevent, f"Error generating image: {str(e)}")
        return None, None

    photos = []
    captions = []
    for i, media in enumerate(response["data"], 1):
        photo = await wall_download(media["url"], "Dall-E")
        photos.append(photo)
        captions.append("")
        await edit_or_reply(catevent, f"__📥 Downloaded : {i}/{limit}__")

    captions[-1] = f"**➥ Query :-** `{text.title()}`"
    await edit_or_reply(catevent, "__Uploading...__")
    return photos, captions


class ThabAi:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "authority": "chatbot.theb.ai",
            "content-type": "application/json",
            "origin": "https://chatbot.theb.ai",
            "user-agent": UserAgent().random,
        }

    def get_response(self, prompt: str) -> str:
        response = self.session.post(
            "https://chatbot.theb.ai/api/chat-process",
            json={"prompt": prompt, "options": {}},
            stream=True,
        )
        response.raise_for_status()
        response_lines = response.iter_lines()
        response_data = ""
        for line in response_lines:
            if line:
                data = json.loads(line)
                if "utterances" in data:
                    response_data += " ".join(
                        utterance["text"] for utterance in data["utterances"]
                    )
                elif "delta" in data:
                    response_data += data["delta"]
        return response_data
