# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from localization import get_help

__doc__ = get_help("tools")

import contextlib
import os
from glob import glob
from io import BytesIO

from database.helpers import get_random_color
from telethon.errors import MessageTooLongError
from telethon.tl import TLObject

from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.errors import UserBotError
from core.decorators import owner_and_sudos
from core import HNDLR
from core.remote import rm
from utilities.tools import atranslate, json_parser

from .. import LOGS, get_string, humanbytes, ultroid_cmd


@ultroid_cmd(pattern="tr( (.*)|$)", manager=True)
async def tr_func(event):
    input_ = event.pattern_match.group(1).strip().split(maxsplit=1)
    txt = input_[1] if len(input_) > 1 else None
    if input_:
        input_ = input_[0]
    if txt:
        text = txt
    elif event.is_reply:
        message = await event.get_reply_message()
        text = message.message
    else:
        return await event.eor(
            f"`{HNDLR}tr LanguageCode` as reply to a message", time=5
        )
    lan = input_ or "en"
    try:
        tt, det = await atranslate(text, target=lan, detect=True)
        output_str = f"**TRANSLATED** to `{lan}` from `{det}`\n{tt}"
        await event.eor(output_str)
    except Exception as exc:
        LOGS.exception(exc)
        await event.eor(str(exc), time=5)


@ultroid_cmd(
    pattern="id( (.*)|$)",
    manager=True,
)
async def id_func(event):
    text = f"`Sender ID`: `{event.sender_id}`\n"
    if match := event.pattern_match.group(1).strip():
        try:
            ids = await event.client.parse_id(match)
        except Exception as er:
            return await event.eor(str(er))
        if str(ids).startswith("-"):
            text += f"`Requested Chat ID`: "
        else:
            text += f"`Requested User ID`: "
        text += f"`{ids}`\n"
    if reply := (await event.get_reply_message()):
        text += f"`Replied to message ID`: `{reply.id}`\n"
        text += f"`Replied to User ID`: `{reply.sender_id}`\n"
    text += f"`Current Chat ID`: `{event.chat_id}`"
    await event.eor(text)


@ultroid_cmd(pattern="json( (.*)|$)")
async def json_func(event):
    reply_to_id = None
    match = event.pattern_match.group(1).strip()
    if event.reply_to_msg_id:
        msg = await event.get_reply_message()
        reply_to_id = event.reply_to_msg_id
    else:
        msg = event
        reply_to_id = event.message.id
    if (
        match
        and (event.sender_id in owner_and_sudos(only_full=True))
        and hasattr(msg, match.split()[0].split(".")[0])
    ):
        for attr in match.split()[0].split("."):
            msg = getattr(msg, attr, None)
            if not msg:
                break
        with contextlib.suppress(Exception):
            if hasattr(msg, "to_json"):
                msg = msg.to_json(ensure_ascii=False, indent=1)
            elif hasattr(msg, "to_dict"):
                msg = json_parser(msg.to_dict(), indent=1)
            else:
                msg = TLObject.stringify(msg)
        msg = str(msg)
    else:
        msg = json_parser(msg.to_json(), indent=1)
    if "-t" in match:
        with contextlib.suppress(Exception):
            data = json_parser(msg)  # type: ignore
            msg = json_parser(
                {key: data[key] for key in data if data.get(key)}, indent=1
            )
    msg = str(msg)
    if len(msg) > 4096:
        with BytesIO(msg.encode()) as out_file:
            out_file.name = "json-ult.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                reply_to=reply_to_id,
            )
            await event.delete()
        return
    await event.eor(f"```{msg or None}```")


@ultroid_cmd(
    pattern="ls($| ?(.*))",
)
async def ls_func(e):
    """list files in a directory"""
    files = e.pattern_match.group(1).strip()
    if not files:
        files = "*"
    elif files.endswith("/"):
        files += "*"
    elif "*" not in files:
        files += "/*"
    files = glob(files)

    if not files:
        return await e.eor("`Directory Empty or Incorrect.`", time=5)
    pyfiles = []
    jsons = []
    vdos = []
    audios = []
    pics = []
    others = []
    otherfiles = []
    folders = []
    text = []
    apk = []
    exe = []
    zip_ = []
    book = []
    for file in sorted(files):
        if os.path.isdir(file):
            folders.append(f"📂 {str(file)}")
        elif str(file).endswith(".py"):
            pyfiles.append(f"🐍 {str(file)}")
        elif str(file).endswith(".json"):
            jsons.append(f"🔮 {str(file)}")
        elif str(file).endswith((".mkv", ".mp4", ".avi", ".gif", "webm")):
            vdos.append(f"🎥 {str(file)}")
        elif str(file).endswith((".mp3", ".ogg", ".m4a", ".opus")):
            audios.append(f"🔊 {str(file)}")
        elif str(file).endswith((".jpg", ".jpeg", ".png", ".webp", ".ico")):
            pics.append(f"🖼 {str(file)}")
        elif str(file).endswith((".txt", ".text", ".log")):
            text.append(f"📄 {str(file)}")
        elif str(file).endswith((".apk", ".xapk")):
            apk.append(f"📲 {str(file)}")
        elif str(file).endswith((".exe", ".iso")):
            exe.append(f"⚙ {str(file)}")
        elif str(file).endswith((".zip", ".rar")):
            zip_.append("🗜 " + str(file))
        elif str(file).endswith((".pdf", ".epub")):
            book.append("📗 " + str(file))
        elif "." in str(file)[1:]:
            others.append("🏷 " + str(file))
        else:
            otherfiles.append("📒 " + str(file))
    omk = [
        *sorted(folders),
        *sorted(pyfiles),
        *sorted(jsons),
        *sorted(zip_),
        *sorted(vdos),
        *sorted(pics),
        *sorted(audios),
        *sorted(apk),
        *sorted(exe),
        *sorted(book),
        *sorted(text),
        *sorted(others),
        *sorted(otherfiles),
    ]
    text = ""
    fls, fos = 0, 0
    flc, foc = 0, 0
    for i in omk:
        with contextlib.suppress(BaseException):
            emoji = i.split()[0]
            name = i.split(maxsplit=1)[1]
            nam = name.split("/")[-1]
            if os.path.isdir(name):
                size = 0
                for path, dirs, files in os.walk(name):
                    for f in files:
                        fp = os.path.join(path, f)
                        size += os.path.getsize(fp)
                if humanbytes(size):
                    text += emoji + f" `{nam}`" + "  `" + humanbytes(size) + "`\n"
                    fos += size
                else:
                    text += emoji + f" `{nam}`" + "\n"
                foc += 1
            else:
                if humanbytes(int(os.path.getsize(name))):
                    text += (
                        emoji
                        + f" `{nam}`"
                        + "  `"
                        + humanbytes(int(os.path.getsize(name)))
                        + "`\n"
                    )
                    fls += int(os.path.getsize(name))
                else:
                    text += emoji + f" `{nam}`" + "\n"
                flc += 1
    tfos, tfls, ttol = humanbytes(fos), humanbytes(fls), humanbytes(fos + fls)
    text += f"\n\n`Folders` :  `{foc}` :   `{tfos}`\n`Files` :       `{flc}` :   `{tfls}`\n`Total` :       `{flc+foc}` :   `{ttol}`"
    try:
        await e.eor(text)
    except MessageTooLongError:
        with BytesIO(str.encode(text)) as out_file:
            out_file.name = "output.txt"
            await e.reply(f"`{e.text}`", file=out_file)
        await e.delete()


# TODO: fix it a bit


@ultroid_cmd(
    pattern="graph( ?(.*)|$)",
)
async def graph_func(event):
    """
    `graph`
    `graph list`"""
    input_str = event.pattern_match.group(1).strip()
    xx = await event.eor(get_string("com_1"))
    with rm.get("graph", helper=True, dispose=True) as mod:
        upload_file, client = mod.upload_file, mod.get_client()
    if event.reply_to_msg_id:
        getmsg = await event.get_reply_message()
        if getmsg.photo or getmsg.video or getmsg.gif:
            getit = await getmsg.download_media()
            try:
                nn = upload_file(getit)
                os.remove(getit)
                amsg = f"Uploaded to [Telegraph]({nn}) !"
            except Exception as e:
                amsg = f"Error - {e}"
            return await xx.edit(amsg)
        elif getmsg.document:
            getit = await getmsg.download_media()
            with open(getit, "r") as ab:
                cd = ab.read()
            os.remove(getit)
        elif getmsg.text:
            cd = getmsg.text
        else:
            return await xx.edit("Reply to a Media or Text !")
        tcom = input_str or "Ultroid"
        makeit = client.create_page(title=tcom, content=[cd])
        war = makeit["url"]
        await xx.edit(f"Pasted to Telegraph : [Telegraph]({war})")
        return
    elif input_str == "list":
        res = client.get_page_list()
        if not res["total_count"]:
            return await xx.edit("`You have not created any telegraph.`")
        text = "**Telegraph Pages**\n\n"
        for page in res["pages"]:
            text += f"- [{page['title']}]({page['url']}) ({page['views']})\n"
        await xx.edit(text)
        return
    await xx.edit("Reply to a Message !")


@ultroid_cmd(pattern="q( (.*)|$)", manager=True, allow_pm=True)
async def q_func(event):
    match = event.pattern_match.group(1).strip()
    if not event.is_reply:
        return await event.eor("`Reply to Message..`")
    msg = await event.eor(get_string("com_1"))
    reply = await event.get_reply_message()
    replied_to, reply_ = None, None
    if match:
        spli_ = match.split(maxsplit=1)
        if (spli_[0] in ["r", "reply"]) or (
            spli_[0].isdigit() and int(spli_[0]) in range(1, 21)
        ):
            if spli_[0].isdigit():
                if not event.client._bot:
                    reply_ = await event.client.get_messages(
                        event.chat_id,
                        min_id=event.reply_to_msg_id - 1,
                        reverse=True,
                        limit=int(spli_[0]),
                    )
                else:
                    id_ = reply.id
                    reply_ = []
                    for msg_ in range(id_, id_ + int(spli_[0])):
                        msh = await event.client.get_messages(event.chat_id, ids=msg_)
                        if msh:
                            reply_.append(msh)
            else:
                replied_to = await reply.get_reply_message()
            try:
                match = spli_[1]
            except IndexError:
                match = None
    user = None
    if not reply_:
        reply_ = reply
    if match:
        match = match.split(maxsplit=1)
    if match:
        if match[0].startswith("@") or match[0].isdigit():
            try:
                match_ = await event.client.parse_id(match[0])
                user = await event.client.get_entity(match_)
            except ValueError:
                pass
            match = match[1] if len(match) == 2 else None
        else:
            match = match[0]
    if match == "random":
        match = get_random_color()
    try:
        with rm.get("quotly", helper=True, dispose=True) as mod:
            file = await mod.create_quotly(
                reply_, bg=match, reply=replied_to, sender=user
            )
    except Exception as er:
        return await msg.edit(str(er))
    message = await reply.reply("Quotly by Ultroid", file=file)
    os.remove(file)
    await msg.delete()
    return message


@ultroid_cmd(
    pattern="invite( (.*)|$)",
    groups_only=True,
)
async def invite_func(ult):
    xx = await ult.eor(get_string("com_1"))
    to_add_users = ult.pattern_match.group(1).strip()
    add_chat_user = not ult.is_channel and ult.is_group
    request = AddChatUserRequest if add_chat_user else InviteToChannelRequest
    users = to_add_users.split()
    single = len(users) == 1

    for user_id in users:
        try:
            if add_chat_user:
                kwargs = {
                    "chat_id": ult.chat_id,
                    "user_id": await ult.client.parse_id(user_id),
                    "fwd_limit": 1000000,
                }
            else:
                kwargs = {
                    "channel": ult.chat_id,
                    "users": [await ult.client.parse_id(user_id)],
                }
            await ult.client(request(**kwargs))
            await xx.edit(f"Successfully invited `{user_id}` to `{ult.chat_id}`")
        except UserBotError as er:
            if single:
                await xx.edit(
                    f"Bots can only be added as Admins in Channel.\nBetter Use `{HNDLR}promote {user_id}`"
                )
                continue
            LOGS.exception(er)
        except Exception as er:
            if single:
                await xx.edit(str(er))
                continue
            LOGS.exception(er)
