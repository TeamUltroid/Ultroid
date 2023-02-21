# Ported From DarkCobra , Originally By Uniborg
# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

• `{i}clone <reply/username>`
    clone the identity of user.

• `{i}revert`
    Revert to your original identity
"""

import html

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName

from . import *


@ultroid_cmd(pattern="clone ?(.*)", fullsudo=True)
async def _(event):
    eve = await event.eor("`Processing...`")
    reply_message = await event.get_reply_message()
    whoiam = await event.client(GetFullUserRequest(ultroid_bot.uid))
    if whoiam.full_user.about:
        mybio = str(ultroid_bot.me.id) + "01"
        udB.set_key(f"{mybio}", whoiam.full_user.about)  # saving bio for revert
    udB.set_key(f"{ultroid_bot.uid}02", whoiam.users[0].first_name)
    if whoiam.users[0].last_name:
        udB.set_key(f"{ultroid_bot.uid}03", whoiam.users[0].last_name)
    replied_user, error_i_a = await get_full_user(event)
    if replied_user is None:
        await eve.edit(str(error_i_a))
        return
    user_id = replied_user.users[0].id
    profile_pic = await event.client.download_profile_photo(user_id)
    first_name = html.escape(replied_user.users[0].first_name)
    if first_name is not None:
        first_name = first_name.replace("\u2060", "")
    last_name = replied_user.users[0].last_name
    if last_name is not None:
        last_name = html.escape(last_name)
        last_name = last_name.replace("\u2060", "")
    if last_name is None:
        last_name = "⁪⁬⁮⁮⁮"
    user_bio = replied_user.full_user.about
    await event.client(UpdateProfileRequest(first_name=first_name))
    await event.client(UpdateProfileRequest(last_name=last_name))
    await event.client(UpdateProfileRequest(about=user_bio))
    if profile_pic:
        pfile = await event.client.upload_file(profile_pic)
        await event.client(UploadProfilePhotoRequest(pfile))
    await eve.delete()
    await event.client.send_message(
        event.chat_id, f"**I am `{first_name}` from now...**", reply_to=reply_message
    )


@ultroid_cmd(pattern="revert$")
async def _(event):
    name = OWNER_NAME
    ok = ""
    mybio = str(ultroid_bot.me.id) + "01"
    bio = "Error : Bio Lost"
    chc = udB.get_key(mybio)
    if chc:
        bio = chc
    fname = udB.get_key(f"{ultroid_bot.uid}02")
    lname = udB.get_key(f"{ultroid_bot.uid}03")
    if fname:
        name = fname
    if lname:
        ok = lname
    n = 1
    client = event.client
    await client(
        DeletePhotosRequest(await event.client.get_profile_photos("me", limit=n))
    )
    await client(UpdateProfileRequest(about=bio))
    await client(UpdateProfileRequest(first_name=name))
    await client(UpdateProfileRequest(last_name=ok))
    await event.eor("Succesfully reverted to your account back !")
    udB.del_key(f"{ultroid_bot.uid}01")
    udB.del_key(f"{ultroid_bot.uid}02")
    udB.del_key(f"{ultroid_bot.uid}03")


async def get_full_user(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.forward:
            replied_user = await event.client(
                GetFullUserRequest(
                    previous_message.forward.sender_id
                    or previous_message.forward.channel_id
                )
            )
            return replied_user, None
        replied_user = await event.client(
            GetFullUserRequest(previous_message.sender_id)
        )
        return replied_user, None
    else:
        input_str = None
        try:
            input_str = event.pattern_match.group(1)
        except IndexError as e:
            return None, e
        if event.message.entities is not None:
            mention_entity = event.message.entities
            probable_user_mention_entity = mention_entity[0]
            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            try:
                user_object = await event.client.get_entity(input_str)
                user_id = user_object.id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e
        elif event.is_private:
            try:
                user_id = event.chat_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e
        else:
            try:
                user_object = await event.client.get_entity(int(input_str))
                user_id = user_object.id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user, None
            except Exception as e:
                return None, e
