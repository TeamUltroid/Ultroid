import json
import os
from json.decoder import JSONDecodeError

from aiohttp import web
from aiohttp.http_websocket import WSMsgType
from pyUltroid import Var, vcbot
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.phone import (GetGroupCallRequest,
                                         JoinGroupCallRequest)
from telethon.tl.types import DataJSON

bot = TelegramClient(None, Var.API_ID, Var.API_HASH).start(bot_token=Var.BOT_TOKEN)


if vcbot:

    async def get_entity(chat):
        try:
            return await vcbot.get_input_entity(chat["id"])
        except ValueError:
            if "username" in chat:
                return await vcbot.get_entity(chat["username"])
            raise

    async def join_call(data):
        try:
            chat = await get_entity(data["chat"])
        except Exception as ex:
            return await bot.send_message(data["chat"]["id"], "`" + str(ex) + "`")
        try:
            full_chat = await vcbot(GetFullChannelRequest(chat))
        except Exception as ex:
            return await bot.send_message(data["chat"]["id"], "`" + str(ex) + "`")
        try:
            call = await vcbot(GetGroupCallRequest(full_chat.full_chat.call))
        except:
            call = None
        if not call:
            return await bot.send_message(
                data["chat"]["id"],
                "`I can't access voice chat.`",
            )

        try:
            result = await vcbot(
                JoinGroupCallRequest(
                    call=call.call,
                    muted=False,
                    join_as="me",
                    params=DataJSON(
                        data=json.dumps(
                            {
                                "ufrag": data["ufrag"],
                                "pwd": data["pwd"],
                                "fingerprints": [
                                    {
                                        "hash": data["hash"],
                                        "setup": data["setup"],
                                        "fingerprint": data["fingerprint"],
                                    },
                                ],
                                "ssrc": data["source"],
                            },
                        ),
                    ),
                ),
            )
            await bot.send_message(
                Var.LOG_CHANNEL,
                f"`Joined Voice Chat in {(await bot.get_entity(data['chat']['id'])).title}`",
            )
        except ChannelPrivateError:
            stree = (await vcbot.get_me()).first_name
            return await bot.send_message(
                data["chat"]["id"], f"Please add {stree} in this group.`"
            )
        except Exception as ex:
            return await bot.send_message(data["chat"]["id"], "`" + str(ex) + "`")

        transport = json.loads(result.updates[0].call.params.data)["transport"]

        return {
            "_": "get_join",
            "data": {
                "chat_id": data["chat"]["id"],
                "transport": {
                    "ufrag": transport["ufrag"],
                    "pwd": transport["pwd"],
                    "fingerprints": transport["fingerprints"],
                    "candidates": transport["candidates"],
                },
            },
        }

    #    async def leave_vc(data):
    #        await bot.send_message(Var.LOG_CHANNEL, "Received Leave Request")
    #        try:
    #            await get_entity(data["chat"]["id"])
    #        except Exception as ex:
    #            return await bot.send_message(data["chat"]["id"], "`" + str(ex) + "`")
    #        try:
    #            full_chat = await vcbot(GetFullChannelRequest(chat))
    #        except Exception as ex:
    #            return await bot.send_message(data["chat"]["id"], "`" + str(ex) + "`")
    #        try:
    #            call = await vcbot(GetGroupCallRequest(full_chat.full_chat.call))
    #        except:
    #            call = None
    #
    #        try:
    #            result = await vcbot(
    #                LeaveGroupCallRequest(
    #                    call=call.call,
    #                    source=data["source"],
    #                ),
    #            )
    #            await bot.send_message(
    #                Var.LOG_CHANNEL,
    #                f"`Left Voice Chat in {(await bot.get_entity(data['chat']['id'])).title}`",
    #            )
    #        except Exception as ex:
    #            return await bot.send_message(data["chat"]["id"], "`" + str(ex) + "`")
    #
    #        return {"_": "left_vc", "data": {"chat_id": data["chat"]["id"]}}

    async def websocket_handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except JSONDecodeError:
                    await ws.close()
                    break

                response = None
                if data["_"] == "join":
                    response = await join_call(data["data"])

                #                if data["_"] == "leave":
                #                    response = await leave_vc(data["data"])

                if response is not None:
                    await ws.send_json(response)

        return ws

    def main():
        app = web.Application()
        app.router.add_route("GET", "/", websocket_handler)
        web.run_app(app, port=os.environ.get("PORT", 6969))

    vcbot.start()
    main()
