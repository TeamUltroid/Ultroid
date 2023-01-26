import os, sys
from core.setup import LOGS
from core.config import HOSTED_ON
from .base_db import BaseDatabase

from redis import Redis

class RedisDB(BaseDatabase):
    def __init__(
        self,
        host,
        port,
        password,
        logger=LOGS,
        *args,
        **kwargs,
    ):
        if host and ":" in host:
            spli_ = host.split(":")
            host = spli_[0]
            port = int(spli_[-1])
            if host.startswith("http"):
                logger.error("Your REDIS_URI should not start with http !")

                sys.exit()
        elif not host or not port:
            logger.error("Port Number not found")

            sys.exit()
        kwargs["host"] = host
        kwargs["password"] = password
        kwargs["port"] = port

        if not host and HOSTED_ON.lower() == "qovery":
            var, hash_, host, password = "", "", "", ""
            for vars_ in os.environ:
                if vars_.startswith("QOVERY_REDIS_") and vars.endswith("_HOST"):
                    var = vars_
            if var:
                hash_ = var.split("_", maxsplit=2)[1].split("_")[0]
            if hash:
                kwargs["host"] = os.environ.get(f"QOVERY_REDIS_{hash_}_HOST")
                kwargs["port"] = os.environ.get(f"QOVERY_REDIS_{hash_}_PORT")
                kwargs["password"] = os.environ.get(f"QOVERY_REDIS_{hash_}_PASSWORD")
        self.db = Redis(**kwargs)
        self.delete = self.db.delete
        self.set = self.db.set 
        self.keys = self.db.keys
        self.get = self.db.get
        super().__init__(**kwargs)

    @property
    def name(self):
        return "Redis"

    @property
    def usage(self):
        return sum(self.db.memory_usage(x) for x in self.keys())

Database = RedisDB