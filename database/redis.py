import os
import re
import sys

from core.config import HOSTED_ON
from core.setup import LOGS
from redis import Redis

from .base_db import BaseDatabase


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
            self._fill_qovery(kwargs)
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

    def _fill_qovery(self, kwargs):
        def _get_match(e):
            return re.match("QOVERY_REDIS_(.*)_HOST", e)

        sort = list(filter(lambda e: re.match("QOVERY_REDIS_(.*)_HOST", e), os.environ))
        if not sort:
            return
        hash_ = _get_match(sort[-1]).group(1)
        if not hash_:
            return
        kwargs["host"] = os.environ.get(f"QOVERY_REDIS_{hash_}_HOST")
        kwargs["port"] = os.environ.get(f"QOVERY_REDIS_{hash_}_PORT")
        kwargs["password"] = os.environ.get(f"QOVERY_REDIS_{hash_}_PASSWORD")


Database = RedisDB
