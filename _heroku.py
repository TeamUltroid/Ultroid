import heroku3
from core import Var, LOGS

client = heroku3.from_api(Var.HEROKU_API)
try:
    app = heroku3.apps()[Var.HEROKU_APP_NAME]
except Exception as er:
    LOGS.exception(er)
    app = None

def restart():
    if app:
        app.restart()

def update():
    # TODO