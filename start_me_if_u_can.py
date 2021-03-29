import json
import os
from json.decoder import JSONDecodeError

from aiohttp import web
from aiohttp.http_websocket import WSMsgType
from pyUltroid import vcbot, ultroid_bot as bot
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.phone import GetGroupCallRequest, JoinGroupCallRequest
from telethon.tl.types import DataJSON

if vcbot:

    async def get_entity(chat):
        try:
            return await vcbot.get_input_entity(chat["id"])
        except ValueError:
            if "username" in chat:
                return await vcbot.get_entity(chat["username"])
            raise

    async def leave_call(data, text):
        try:
            await bot.asst.send_message(
                entity=data['chat']['id'],
                message=text,
            )
        except:
            pass
        try:
            await bot.asst.delete_dialog(
                entity=data['chat']['id']
            )
        except:
            pass

    async def join_call(data):
        try:
            chat = await get_entity(data["chat"])
            full_chat = await vcbot(GetFullChannelRequest(chat))
            call = await vcbot(GetGroupCallRequest(full_chat.full_chat.call))
        except Exception as ex:
            return await leave_call(data, "`" + str(ex) + "`")

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
                                }
                            ],
                            "ssrc": data["source"],
                        }
                    ),
                ),
            ),
        )

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

                if response is not None:
                    await ws.send_json(response)

        return ws

    def main():
        app = web.Application()
        app.router.add_route("GET", "/", websocket_handler)
        web.run_app(app, port=os.environ.get("PORT", 6969))

    vcbot.start()
    main()
