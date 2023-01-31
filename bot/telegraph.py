from contextlib import suppress
from database import udB
from utilities.helper import run_async
from core import ultroid_bot, LOGS
from telegraph import Telegraph

def get_client():
    _api = udB.get_key("_TELEGRAPH_TOKEN")
    client = Telegraph(_api, domain="graph.org")
    if not _api:
        gd_name = ultroid_bot.full_name
        short_name = gd_name[:30]
        profile_url = (
            f"https://t.me/{ultroid_bot.me.username}"
            if ultroid_bot.me.username
            else "https://t.me/TeamUltroid"
        )
        try:
            client.create_account(
                short_name=short_name, author_name=gd_name, author_url=profile_url
            )
        except Exception as er:
            if "SHORT_NAME_TOO_LONG" in str(er):
                client.create_account(
                    short_name="ultroiduser", author_name=gd_name, author_url=profile_url
                )
            LOGS.exception(er)
        if _token := client.get_access_token():
            udB.set_key("_TELEGRAPH_TOKEN", _token)
    return client

def upload_file(path):
    if path.endswith("webp"):
        with suppress(ImportError):
            from PIL import Image
            Image.open(path).save(path, "PNG")
    return f"https://graph.org{get_client().upload_file(path)[-1]}"



@run_async
def make_html_telegraph(title, html=""):
    telegraph = get_client()
    page = telegraph.create_page(
        title=title,
        html_content=html,
    )
    return page["url"]
