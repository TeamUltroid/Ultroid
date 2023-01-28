import os, math, shutil, psutil
from random import choice
from utilities import some_random_headers
from utilities.helper import async_searcher, humanbytes
import heroku3
from core import Var, LOGS
from localization import get_string

client = heroku3.from_api(Var.HEROKU_API)
try:
    app = heroku3.app(Var.HEROKU_APP_NAME)
except Exception as er:
    LOGS.exception(er)
    app = None


def restart():
    if app:
        app.restart()


def update():
    # TODO
    pass


async def shutdown(event):
    if not app:
        return await event.edit("`Cant detect as Heroku App!\nValidate your` `HEROKU_API` `and` `HEROKU_API_KEY`, `check for logs`")
    dynotype = Var.DYNO.split(".")[-1]
    await event.edit("Shutting down.")
    try:
        app.process_formation()[dynotype].scale(0)
    except Exception as er:
        LOGS.exception(er)
        await event.edit(f"Something went wrong!\n{er}")


async def heroku_logs(event):
    """
    post heroku logs
    """

    xx = await event.eor("`Processing...`")
    if not (Var.HEROKU_API and Var.HEROKU_APP_NAME):
        return await xx.edit("Please set `HEROKU_APP_NAME` and `HEROKU_API` in vars.")
    elif not app:
        return await xx.edit(
            "`HEROKU_API` and `HEROKU_APP_NAME` is wrong! Kindly re-check in config vars."
        )
    await xx.edit("`Downloading Logs...`")
    ok = app.get_log()
    with open("ultroid-heroku.log", "w") as log:
        log.write(ok)
    await event.client.send_file(
        event.chat_id,
        file="ultroid-heroku.log",
        caption="**Ultroid Heroku Logs.**",
    )

    os.remove("ultroid-heroku.log")
    await xx.delete()


async def heroku_usage():

    user_id = Heroku.account().id
    headers = {
        "User-Agent": choice(some_random_headers),
        "Authorization": f"Bearer {}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    her_url = f"https://api.heroku.com/accounts/{user_id}/actions/get-quota"
    try:
        result = await async_searcher(her_url, headers=headers, re_json=True)
    except Exception as er:
        return False, str(er)
    quota = result["account_quota"]
    quota_used = result["quota_used"]
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)
    total, used, free = shutil.disk_usage(".")
    _ = shutil.disk_usage("/")
    disk = _.used / _.total * 100
    cpuUsage = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    upload = humanbytes(psutil.net_io_counters().bytes_sent)
    down = humanbytes(psutil.net_io_counters().bytes_recv)
    TOTAL = humanbytes(total)
    USED = humanbytes(used)
    FREE = humanbytes(free)
    return True, get_string("usage").format(
        Var.HEROKU_APP_NAME,
        AppHours,
        AppMinutes,
        AppPercentage,
        hours,
        minutes,
        percentage,
        TOTAL,
        USED,
        FREE,
        upload,
        down,
        cpuUsage,
        memory,
        disk,
    )
