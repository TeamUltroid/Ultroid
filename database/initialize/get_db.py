from core.config import Var, HOSTED_ON
from core.remote import rm
from core.setup import LOGS


def getDatabase():
    args, kwargs = (), {}

    if Var.REDIS_URI or Var.REDIS_HOST:
        args = (Var.REDIS_URI or Var.REDISHOST, Var.REDISPORT)
        kwargs = {
            "password": Var.REDIS_PASSWORD or Var.REDISPASSWORD,
            "decode_responses": True,
            "socket_timeout": 5,
            "retry_on_timeout": True,
        }
        key = "redisdb"
    elif Var.MONGO_URI and not HOSTED_ON == "termux":
        args, key = [Var.MONGO_URI], "mongodb"
    elif Var.DATABASE_URL:
        args, key = [Var.DATABASE_URI], "sql"
    elif HOSTED_ON == "termux":
        if Var.MONGO_URI:
            LOGS.critical("MongoDB is not compatible with termux! kindly use another database.\ncontinuing with localdb.")
        args, key = (), "local"
    else:
        LOGS.critical(
            "No DB requirement fullfilled!\nPlease install redis, mongo or sql dependencies...\nTill then using local file as database."
        )
        args, key = (), "local"
    with rm.get(key, f"database/initialize/{key}.py", helper=True) as db:
        if db:
            return db.Database(*args, **kwargs)
