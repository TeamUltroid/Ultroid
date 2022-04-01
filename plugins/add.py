import time
from pyrogram import filters
from userbot import UserBot
from userbot.helpers.PyroHelpers import GetChatID
from userbot.plugins.help import add_command_help
from pyrogram.raw import functions

@UserBot.on_message(filters.me & filters.text & filters.command("add_members","."))
async def hi(client, message):
    cmd = message.command
    fromgroup = cmd[1]
    togroup = cmd[2]
    if len(fromgroup) > 0 and len(togroup) > 0:
        async def GetCommon(get_user):
            common = await client.send(
                functions.messages.GetCommonChats(
                    user_id=await client.resolve_peer(get_user), max_id=0, limit=0
                )
            )
            return common
        failed = 0
        added = 0
        already = 0
        d = await client.send_message(chat_id=message.chat["id"], reply_to_message_id=int(message.message_id), text="adding members\nadded : " + str(added))
        msgid = d.message_id
        chatid = d.chat['id']
        comd = message.message_id
        comdchat = message.chat['id']
        tog = cmd[2].split("@")[1]
        async for member in client.iter_chat_members(fromgroup):
            msg = await client.get_messages(comdchat,comd)
            common = await GetCommon(member.user.id)
            try:
                if msg.text == None:
                    await d.reply("message is deleted member adding is stopped")
                    break
                else:
                    if member.user.is_bot == False and f'"username": "{tog}"' not in str(common): #.is_bot == False:
                        print("before add")
                        status = await client.add_chat_members(togroup, int(member.user.id))
                        # print(status)
                        print("after add")
                        if status:
                            await client.edit_message_text(chatid,msgid,"adding members" + "\nalready : " + str(already)+"\nadded : " + str(added) + "\nfailed : " + str(failed))
                            added += 1
                        else:
                            await client.edit_message_text(chatid,msgid,"adding members" + "\nalready : " + str(already)+"\nadded : " + str(added) + "\nfailed : " + str(failed))
                            failed += 1
                    else:
                        await client.edit_message_text(chatid,msgid,"adding members" + "\nalready : " + str(already)+"\nadded : " + str(added) + "\nfailed : " + str(failed))
                        already += 1
            except Exception as error:
                if "CHAT_ADMIN_REQUIRED" in str(error):
                    await client.send_message(chat_id=message.chat["id"], reply_to_message_id=int(message.message_id), text="CHAT_ADMIN_REQUIRED")
                    failed += 1
                elif "BROADCAST_FORBIDDEN" in str(error):
                    # await client.send_message(chat_id=message.chat["id"], reply_to_message_id=int(message.message_id), text="BROADCAST_FORBIDDEN")
                    failed += 1
                elif "CHANNEL_PUBLIC_GROUP_NA" in str(error):
                    # await client.send_message(chat_id=message.chat["id"], reply_to_message_id=int(message.message_id), text="CHANNEL_PUBLIC_GROUP_NA")
                    failed += 1
                elif "CHAT_ADMIN_INVITE_REQUIRED" in str(error):
                    # await client.send_message(chat_id=message.chat["id"], reply_to_message_id=int(message.message_id), text="CHAT_ADMIN_INVITE_REQUIRED")
                    failed += 1
                elif "CHAT_FORBIDDEN" in str(error):
                    # await client.send_message(chat_id=message.chat["id"], reply_to_message_id=int(message.message_id), text="CHAT_FORBIDDEN")
                    failed += 1
                elif "USER_NOT_MUTUAL_CONTACT" in str(error):
                    # await client.send_message(chat_id=message.chat["id"], reply_to_message_id=int(message.message_id), text="USER_NOT_MUTUAL_CONTACT")
                    failed += 1
                elif "USER_PRIVACY_RESTRICTED" in str(error):
                    failed += 1
                    continue
                elif "account is currently limited" in str(error):
                    await client.send_message(chat_id=message.chat["id"], reply_to_message_id=int(message.message_id), text="The account is currently limited for this action restart bot and try later")
                    failed += 1
                    break
                else:
                    await client.send_message(chat_id=message.chat["id"], reply_to_message_id=int(message.message_id), text=str(error))
                    second = await client.send_message(chat_id=chatid,reply_to_message_id=int(message.message_id),text="adding members" + "\talready : " + str(already)+"\nadded : " + str(added) + "\nfailed : " + str(failed))
                continue
        await client.send_message(chat_id=message.chat["id"], reply_to_message_id=int(message.message_id), text="Finished adding members")
    else:
        await client.send_message(chat_id=message.chat["id"], reply_to_message_id=int(message.message_id), text="Invalid arguments")  


      
add_command_help(
    "hackers",
    [
        [
            ".add_members",
            "ADD MEMBERS from one group to other group \nUsage: ``.add_members <from group username> <to group username>``",
        ],
    ],
)