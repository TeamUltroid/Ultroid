from .. import get_string, ultroid_cmd
from telethon.errors.rpcerrorlist import YouBlockedUserError

@ultroid_cmd(
    pattern="sg( (.*)|$)",
)
async def lastname(steal):
    mat = steal.pattern_match.group(1).strip()
    message = await steal.get_reply_message()
    if mat:
        try:
            user_id = await steal.client.parse_id(mat)
        except ValueError:
            user_id = mat
    elif message:
        user_id = message.sender_id
    else:
        return await steal.eor("`Use this command with reply or give Username/id...`")
    chat = "@SangMataInfo_bot"
    id = f"/search_id {user_id}"
    lol = await steal.eor(get_string("com_1"))
    try:
        async with steal.client.conversation(chat) as conv:
            try:
                msg = await conv.send_message(id)
                response = await conv.get_response()
                respond = await conv.get_response()
                responds = await conv.get_response()
            except YouBlockedUserError:
                return await lol.edit("Please unblock @sangmatainfo_bot and try again")
            if (
                (response and response.text == "No records found")
                or (respond and respond.text == "No records found")
                or (responds and responds.text == "No records found")
            ):
                await lol.edit("No records found for this user")
                await steal.client.delete_messages(conv.chat_id, [msg.id, response.id])
            elif response.text.startswith("🔗"):
                await lol.edit(respond.message)
                await lol.reply(responds.message)
            elif respond.text.startswith("🔗"):
                await lol.edit(response.message)
                await lol.reply(responds.message)
            else:
                await lol.edit(respond.message)
                await lol.reply(response.message)
            await steal.client.delete_messages(
                conv.chat_id,
                [msg.id, responds.id, respond.id, response.id],
            )
    except Exception as er:
        await lol.edit("Error: @SangMataInfo_bot is not responding!.")
