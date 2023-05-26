import os, logging
from telethon import TelegramClient
from telethon.sessions import MemorySession


async def start_session_bot(asst=None):
    if not asst:
        from core import asst, LOGS

    else:
        logging.basicConfig(level=logging.INFO)
        LOGS = logging.getLogger()

    # Clean UP
    for i,e in asst.list_event_handlers():
        asst.remove_event_handler(i, e)

    # TODO: add session bot handlers to asst


if __name__ == "__main__":
    BOT_TOKEN = os.getenv("BOT_TOKEN", input("Enter BOT TOKEN: "))
    API_ID = int(os.getenv("API_ID", input("Enter API ID: ")))
    API_HASH = os.getenv("API_HASH", input("Enter API Hash: "))

    client = TelegramClient(MemorySession(), api_id=API_ID, api_hash=API_HASH)
    client.start()
    client.loop.run_until_complete(start_session_bot(client))
    client.run_until_disconnected()