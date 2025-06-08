# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import asyncio
import os
import random
import shutil
import time
from random import randint
import base64
from urllib.parse import unquote

from ..configs import Var

try:
    from pytz import timezone
except ImportError:
    timezone = None

from telethon.errors import (
    ChannelsTooMuchError,
    ChatAdminRequiredError,
    MessageIdInvalidError,
    MessageNotModifiedError,
    UserNotParticipantError,
)
from telethon.tl.custom import Button
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    EditAdminRequest,
    EditPhotoRequest,
    InviteToChannelRequest,
)
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import (
    ChatAdminRights,
    ChatPhotoEmpty,
    InputChatUploadedPhoto,
    InputMessagesFilterDocument,
)
from telethon.utils import get_peer_id
from decouple import config, RepositoryEnv
from telethon import functions
from urllib.parse import urlparse, parse_qs
import json
from datetime import datetime
import requests
from .. import LOGS, ULTConfig
from ..fns.helper import download_file, inline_mention, updater

db_url = 0


async def autoupdate_local_database():
    from .. import Var, asst, udB, ultroid_bot

    global db_url
    db_url = (
        udB.get_key("TGDB_URL") or Var.TGDB_URL or ultroid_bot._cache.get("TGDB_URL")
    )
    if db_url:
        _split = db_url.split("/")
        _channel = _split[-2]
        _id = _split[-1]
        try:
            await asst.edit_message(
                int(_channel) if _channel.isdigit() else _channel,
                message=_id,
                file="database.json",
                text="**Do not delete this file.**",
            )
        except MessageNotModifiedError:
            return
        except MessageIdInvalidError:
            pass
    try:
        LOG_CHANNEL = (
            udB.get_key("LOG_CHANNEL")
            or Var.LOG_CHANNEL
            or asst._cache.get("LOG_CHANNEL")
            or "me"
        )
        msg = await asst.send_message(
            LOG_CHANNEL, "**Do not delete this file.**", file="database.json"
        )
        asst._cache["TGDB_URL"] = msg.message_link
        udB.set_key("TGDB_URL", msg.message_link)
    except Exception as ex:
        LOGS.error(f"Error on autoupdate_local_database: {ex}")


def update_envs():
    """Update Var. attributes to udB"""
    from .. import udB

    _envs = [*list(os.environ)]
    if ".env" in os.listdir("."):
        [_envs.append(_) for _ in list(RepositoryEnv(config._find_file(".")).data)]
    for envs in _envs:
        if (
            envs in ["LOG_CHANNEL", "BOT_TOKEN", "BOTMODE", "DUAL_MODE", "language"]
            or envs in udB.keys()
        ):
            if _value := os.environ.get(envs):
                udB.set_key(envs, _value)
            else:
                udB.set_key(envs, config.config.get(envs))


async def startup_stuff():
    from .. import udB

    x = ["resources/auth", "resources/downloads"]
    for x in x:
        if not os.path.isdir(x):
            os.mkdir(x)

    CT = udB.get_key("CUSTOM_THUMBNAIL")
    if CT:
        path = "resources/extras/thumbnail.jpg"
        ULTConfig.thumb = path
        try:
            await download_file(CT, path)
        except Exception as er:
            LOGS.exception(er)
    elif CT is False:
        ULTConfig.thumb = None
    GT = udB.get_key("GDRIVE_AUTH_TOKEN")
    if GT:
        with open("resources/auth/gdrive_creds.json", "w") as t_file:
            t_file.write(GT)

    if udB.get_key("AUTH_TOKEN"):
        udB.del_key("AUTH_TOKEN")

    MM = udB.get_key("MEGA_MAIL")
    MP = udB.get_key("MEGA_PASS")
    if MM and MP:
        with open(".megarc", "w") as mega:
            mega.write(f"[Login]\nUsername = {MM}\nPassword = {MP}")

    TZ = udB.get_key("TIMEZONE")
    if TZ and timezone:
        try:
            timezone(TZ)
            os.environ["TZ"] = TZ
            time.tzset()
        except AttributeError as er:
            LOGS.debug(er)
        except BaseException:
            LOGS.critical(
                "Incorrect Timezone ,\nCheck Available Timezone From Here https://graph.org/Ultroid-06-18-2\nSo Time is Default UTC"
            )
            os.environ["TZ"] = "UTC"
            time.tzset()


async def autobot():
    from .. import udB, ultroid_bot

    if udB.get_key("BOT_TOKEN"):
        return
    await ultroid_bot.start()
    LOGS.info("MAKING A TELEGRAM BOT FOR YOU AT @BotFather, Kindly Wait")
    who = ultroid_bot.me
    name = who.first_name + "'s Bot"
    if who.username:
        username = who.username + "_bot"
    else:
        username = "ultroid_" + (str(who.id))[5:] + "_bot"
    bf = "@BotFather"
    await ultroid_bot(UnblockRequest(bf))
    await ultroid_bot.send_message(bf, "/cancel")
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, "/newbot")
    await asyncio.sleep(1)
    isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    if isdone.startswith("That I cannot do.") or "20 bots" in isdone:
        LOGS.critical(
            "Please make a Bot from @BotFather and add it's token in BOT_TOKEN, as an env var and restart me."
        )
        import sys

        sys.exit(1)
    await ultroid_bot.send_message(bf, name)
    await asyncio.sleep(1)
    isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    if not isdone.startswith("Good."):
        await ultroid_bot.send_message(bf, "My Assistant Bot")
        await asyncio.sleep(1)
        isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
        if not isdone.startswith("Good."):
            LOGS.critical(
                "Please make a Bot from @BotFather and add it's token in BOT_TOKEN, as an env var and restart me."
            )
            import sys

            sys.exit(1)
    await ultroid_bot.send_message(bf, username)
    await asyncio.sleep(1)
    isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    await ultroid_bot.send_read_acknowledge("botfather")
    if isdone.startswith("Sorry,"):
        ran = randint(1, 100)
        username = "ultroid_" + (str(who.id))[6:] + str(ran) + "_bot"
        await ultroid_bot.send_message(bf, username)
        await asyncio.sleep(1)
        isdone = (await ultroid_bot.get_messages(bf, limit=1))[0].text
    if isdone.startswith("Done!"):
        token = isdone.split("`")[1]
        udB.set_key("BOT_TOKEN", token)
        await enable_inline(ultroid_bot, username)
        LOGS.info(
            f"Done. Successfully created @{username} to be used as your assistant bot!"
        )
    else:
        LOGS.info(
            "Please Delete Some Of your Telegram bots at @Botfather or Set Var BOT_TOKEN with token of a bot"
        )

        import sys

        sys.exit(1)


async def autopilot():
    from .. import asst, udB, ultroid_bot

    channel = udB.get_key("LOG_CHANNEL")
    new_channel = None
    if channel:
        try:
            chat = await ultroid_bot.get_entity(channel)
        except BaseException as err:
            LOGS.exception(err)
            udB.del_key("LOG_CHANNEL")
            channel = None
    if not channel:

        async def _save(exc):
            udB._cache["LOG_CHANNEL"] = ultroid_bot.me.id
            await asst.send_message(
                ultroid_bot.me.id, f"Failed to Create Log Channel due to {exc}.."
            )

        if ultroid_bot._bot:
            msg_ = "'LOG_CHANNEL' not found! Add it in order to use 'BOTMODE'"
            LOGS.error(msg_)
            return await _save(msg_)
        LOGS.info("Creating a Log Channel for You!")
        try:
            r = await ultroid_bot(
                CreateChannelRequest(
                    title="My Ultroid Logs",
                    about="My Ultroid Log Group\n\n Join @TeamUltroid",
                    megagroup=True,
                ),
            )
        except ChannelsTooMuchError as er:
            LOGS.critical(
                "You Are in Too Many Channels & Groups , Leave some And Restart The Bot"
            )
            return await _save(str(er))
        except BaseException as er:
            LOGS.exception(er)
            LOGS.info(
                "Something Went Wrong , Create A Group and set its id on config var LOG_CHANNEL."
            )

            return await _save(str(er))
        new_channel = True
        chat = r.chats[0]
        channel = get_peer_id(chat)
        udB.set_key("LOG_CHANNEL", channel)
    assistant = True
    try:
        await ultroid_bot.get_permissions(int(channel), asst.me.username)
    except UserNotParticipantError:
        try:
            await ultroid_bot(InviteToChannelRequest(int(channel), [asst.me.username]))
        except BaseException as er:
            LOGS.info("Error while Adding Assistant to Log Channel")
            LOGS.exception(er)
            assistant = False
    except BaseException as er:
        assistant = False
        LOGS.exception(er)
    if assistant and new_channel:
        try:
            achat = await asst.get_entity(int(channel))
        except BaseException as er:
            achat = None
            LOGS.info("Error while getting Log channel from Assistant")
            LOGS.exception(er)
        if achat and not achat.admin_rights:
            rights = ChatAdminRights(
                add_admins=True,
                invite_users=True,
                change_info=True,
                ban_users=True,
                delete_messages=True,
                pin_messages=True,
                anonymous=False,
                manage_call=True,
            )
            try:
                await ultroid_bot(
                    EditAdminRequest(
                        int(channel), asst.me.username, rights, "Assistant"
                    )
                )
            except ChatAdminRequiredError:
                LOGS.info(
                    "Failed to promote 'Assistant Bot' in 'Log Channel' due to 'Admin Privileges'"
                )
            except BaseException as er:
                LOGS.info("Error while promoting assistant in Log Channel..")
                LOGS.exception(er)
    if isinstance(chat.photo, ChatPhotoEmpty):
        try:
            photo, _ = await download_file(
                "https://graph.org/file/27c6812becf6f376cbb10.jpg", "channelphoto.jpg"
            )
            ll = await ultroid_bot.upload_file(photo)
            await ultroid_bot(
                EditPhotoRequest(int(channel), InputChatUploadedPhoto(ll))
            )
            os.remove(photo)
        except BaseException as er:
            LOGS.exception(er)


# customize assistant


async def customize():
    from .. import asst, udB, ultroid_bot

    rem = None
    try:
        chat_id = udB.get_key("LOG_CHANNEL")
        if asst.me.photo:
            return
        LOGS.info("Customising Ur Assistant Bot in @BOTFATHER")
        UL = f"@{asst.me.username}"
        if not ultroid_bot.me.username:
            sir = ultroid_bot.me.first_name
        else:
            sir = f"@{ultroid_bot.me.username}"
        file = random.choice(
            [
                "https://graph.org/file/92cd6dbd34b0d1d73a0da.jpg",
                "https://graph.org/file/a97973ee0425b523cdc28.jpg",
                "resources/extras/ultroid_assistant.jpg",
            ]
        )
        if not os.path.exists(file):
            file, _ = await download_file(file, "profile.jpg")
            rem = True
        msg = await asst.send_message(
            chat_id, "**Auto Customisation** Started on @Botfather"
        )
        await asyncio.sleep(1)
        await ultroid_bot.send_message("botfather", "/cancel")
        await asyncio.sleep(1)
        await ultroid_bot.send_message("botfather", "/setuserpic")
        await asyncio.sleep(1)
        isdone = (await ultroid_bot.get_messages("botfather", limit=1))[0].text
        if isdone.startswith("Invalid bot"):
            LOGS.info("Error while trying to customise assistant, skipping...")
            return
        await ultroid_bot.send_message("botfather", UL)
        await asyncio.sleep(1)
        await ultroid_bot.send_file("botfather", file)
        await asyncio.sleep(2)
        await ultroid_bot.send_message("botfather", "/setabouttext")
        await asyncio.sleep(1)
        await ultroid_bot.send_message("botfather", UL)
        await asyncio.sleep(1)
        await ultroid_bot.send_message(
            "botfather", f"✨ Hello ✨!! I'm Assistant Bot of {sir}"
        )
        await asyncio.sleep(2)
        await ultroid_bot.send_message("botfather", "/setdescription")
        await asyncio.sleep(1)
        await ultroid_bot.send_message("botfather", UL)
        await asyncio.sleep(1)
        await ultroid_bot.send_message(
            "botfather",
            f"✨ Powerful Ultroid Assistant Bot ✨\n✨ Master ~ {sir} ✨\n\n✨ Powered By ~ @TeamUltroid ✨",
        )
        await asyncio.sleep(2)
        await msg.edit("Completed **Auto Customisation** at @BotFather.")
        if rem:
            os.remove(file)
        LOGS.info("Customisation Done")
    except Exception as e:
        LOGS.exception(e)


async def plug(plugin_channels):
    from .. import ultroid_bot
    from .utils import load_addons

    if ultroid_bot._bot:
        LOGS.info("Plugin Channels can't be used in 'BOTMODE'")
        return
    if os.path.exists("addons") and not os.path.exists("addons/.git"):
        shutil.rmtree("addons")
    if not os.path.exists("addons"):
        os.mkdir("addons")
    if not os.path.exists("addons/__init__.py"):
        with open("addons/__init__.py", "w") as f:
            f.write("from plugins import *\n\nbot = ultroid_bot")
    LOGS.info("• Loading Plugins from Plugin Channel(s) •")
    for chat in plugin_channels:
        LOGS.info(f"{'•'*4} {chat}")
        try:
            async for x in ultroid_bot.iter_messages(
                chat, search=".py", filter=InputMessagesFilterDocument, wait_time=10
            ):
                plugin = "addons/" + x.file.name.replace("_", "-").replace("|", "-")
                if not os.path.exists(plugin):
                    await asyncio.sleep(0.6)
                    if x.text == "#IGNORE":
                        continue
                    plugin = await x.download_media(plugin)
                    try:
                        load_addons(plugin)
                    except Exception as e:
                        LOGS.info(f"Ultroid - PLUGIN_CHANNEL - ERROR - {plugin}")
                        LOGS.exception(e)
                        os.remove(plugin)
        except Exception as er:
            LOGS.exception(er)


async def ready():
    from .. import asst, udB, ultroid_bot

    chat_id = udB.get_key("LOG_CHANNEL")
    spam_sent = None
    if not udB.get_key("INIT_DEPLOY"):  # Detailed Message at Initial Deploy
        MSG = """🎇 **Thanks for Deploying Ultroid Userbot!**
• Here, are the Some Basic stuff from, where you can Know, about its Usage."""
        PHOTO = "https://graph.org/file/54a917cc9dbb94733ea5f.jpg"
        BTTS = Button.inline("• Click to Start •", "initft_2")
        udB.set_key("INIT_DEPLOY", "Done")
    else:
        MSG = f"**Ultroid has been deployed!**\n➖➖➖➖➖➖➖➖➖➖\n**UserMode**: {inline_mention(ultroid_bot.me)}\n**Assistant**: @{asst.me.username}\n➖➖➖➖➖➖➖➖➖➖\n**Support**: @TeamUltroid\n➖➖➖➖➖➖➖➖➖➖"
        BTTS, PHOTO = None, None
        prev_spam = udB.get_key("LAST_UPDATE_LOG_SPAM")
        if prev_spam:
            try:
                await ultroid_bot.delete_messages(chat_id, int(prev_spam))
            except Exception as E:
                LOGS.info("Error while Deleting Previous Update Message :" + str(E))
        if await updater():
            BTTS = Button.inline("Update Available", "updtavail")

    try:
        spam_sent = await asst.send_message(chat_id, MSG, file=PHOTO, buttons=BTTS)
    except ValueError as e:
        try:
            await (await ultroid_bot.send_message(chat_id, str(e))).delete()
            spam_sent = await asst.send_message(chat_id, MSG, file=PHOTO, buttons=BTTS)
        except Exception as g:
            LOGS.info(g)
    except Exception as el:
        LOGS.info(el)
        try:
            spam_sent = await ultroid_bot.send_message(chat_id, MSG)
        except Exception as ef:
            LOGS.exception(ef)
    if spam_sent and not spam_sent.media:
        udB.set_key("LAST_UPDATE_LOG_SPAM", spam_sent.id)

    try:
        await ultroid_bot(JoinChannelRequest("TheUltroid"))
    except Exception as er:
        LOGS.exception(er)


async def WasItRestart(udb):
    key = udb.get_key("_RESTART")
    if not key:
        return
    from .. import asst, ultroid_bot

    try:
        data = key.split("_")
        who = asst if data[0] == "bot" else ultroid_bot
        await who.edit_message(
            int(data[1]), int(data[2]), "__Restarted Successfully.__"
        )
    except Exception as er:
        LOGS.exception(er)
    udb.del_key("_RESTART")


def _version_changes(udb):
    for _ in [
        "BOT_USERS",
        "BOT_BLS",
        "VC_SUDOS",
        "SUDOS",
        "CLEANCHAT",
        "LOGUSERS",
        "PLUGIN_CHANNEL",
        "CH_SOURCE",
        "CH_DESTINATION",
        "BROADCAST",
    ]:
        key = udb.get_key(_)
        if key and str(key)[0] != "[":
            key = udb.get(_)
            new_ = [
                int(z) if z.isdigit() or (z.startswith("-") and z[1:].isdigit()) else z
                for z in key.split()
            ]
            udb.set_key(_, new_)


async def enable_inline(ultroid_bot, username):
    bf = "BotFather"
    await ultroid_bot.send_message(bf, "/setinline")
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, f"@{username}")
    await asyncio.sleep(1)
    await ultroid_bot.send_message(bf, "Search")
    await ultroid_bot.send_read_acknowledge(bf)


async def user_sync_workflow():
    from .. import udB, ultroid_bot
    from ..configs import CENTRAL_REPO_URL, ADMIN_BOT_USERNAME

    from ..state_config import temp_config_store

    # Check if user data exists in temp config store
    user_data = temp_config_store.get("X-TG-USER")

    if user_data and (user_data.get("id") != ultroid_bot.uid):
        temp_config_store.remove("X-TG-USER")
        temp_config_store.remove(f"X-TG-INIT-DATA-{user_data['id']}")
        temp_config_store.remove(f"X-TG-HASH-{user_data['id']}")

    if user_data:
        user_id = str(user_data["id"])
        # Get encoded data and decode it
        encoded_init_data = temp_config_store.get(f"X-TG-INIT-DATA-{user_id}")
        encoded_hash = temp_config_store.get(f"X-TG-HASH-{user_id}")
        
        # Decode the data
        init_data = base64.b64decode(encoded_init_data.encode()).decode() if encoded_init_data else None
        hash_value = base64.b64decode(encoded_hash.encode()).decode() if encoded_hash else None
        
        return await authenticate_user_request(user_data, init_data, hash_value)

    try:

        url = (await ultroid_bot(functions.messages.RequestWebViewRequest(ADMIN_BOT_USERNAME, ADMIN_BOT_USERNAME, platform="android", from_bot_menu=False, url=CENTRAL_REPO_URL))).url

        # Parse the URL fragment to get webAppData
        fragment = urlparse(url).fragment
        params = parse_qs(fragment)
        tg_web_data_raw = params.get("tgWebAppData", [None])[0]

        # Parse the tgWebAppData parameters
        tg_data_params = parse_qs(tg_web_data_raw) if tg_web_data_raw else {}

        # Extract and parse user data
        user_str = tg_data_params.get("user", [None])[0]
        if not user_str:
            raise Exception("No user data found")

        user = json.loads(unquote(user_str))
        hash_value = tg_data_params.get("hash", [None])[0]

        await authenticate_user_request(user, tg_web_data_raw, hash_value)
    except Exception as e:
        LOGS.exception(e)


async def authenticate_user_request(user: dict, init_data: str, hash_value: str):
    from .. import udB, ultroid_bot
    from ..configs import CENTRAL_REPO_URL, ADMIN_BOT_USERNAME

    from ..state_config import temp_config_store
    try:

        # Prepare user data payload
        user_data = {
            "id": user["id"],
            "first_name": user["first_name"],
            "last_name": user.get("last_name", ""),
            "username": user["username"],
            "language_code": user["language_code"],
            "photo_url": user["photo_url"],
            "last_active": datetime.now().isoformat(),
            "joined_at": datetime.now().isoformat()
        }

        # Encode init data and hash using base64 before storing
        user_id = str(user["id"])
        encoded_init_data = base64.b64encode(init_data.encode()).decode() if init_data else ""
        encoded_hash = base64.b64encode(hash_value.encode()).decode() if hash_value else ""
        
        # Store with user ID as part of the key
        temp_config_store.set(f"X-TG-INIT-DATA-{user_id}", encoded_init_data)
        temp_config_store.set(f"X-TG-HASH-{user_id}", encoded_hash)
        temp_config_store.set("X-TG-USER", user_data)

        # Make PUT request
        response = requests.put(
            f"{CENTRAL_REPO_URL}/api/v1/users/{user['id']}", 
            headers={
                "Content-Type": "application/json",
                "x-telegram-init-data": init_data,
                "x-telegram-hash": hash_value or ""
            },
            json=user_data
        )
        if response.status_code == 200:
            LOGS.info(f"User {user['id']} authenticated successfully")
        else:
            LOGS.error(f"User {user['id']} authentication failed")

    except Exception as e:
        LOGS.exception(e)