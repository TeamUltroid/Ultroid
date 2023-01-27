import os
import heroku3
from core import Var, LOGS

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
