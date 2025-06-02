from .base import BaseDatabase
from redis import Redis
import os
from logging import getLogger
from typing import Optional

logger = getLogger(__name__)


class RedisDB(BaseDatabase):
    def __init__(
        self,
        host="localhost",
        port=6379,
        password="",
        platform="",
        client: Optional[Redis] = None,
        *args,
        **kwargs,
    ):
        if not client:
            self.db = self._setup_client(host, port, password, platform, **kwargs)
        else:
            self.db = client
        self.set = self.db.set
        self.get = self.db.get
        self.keys = self.db.keys
        self.delete = self.db.delete
        super().__init__()

    @property
    def name(self):
        return "Redis"

    @property
    def usage(self):
        return sum(self.db.memory_usage(x) for x in self.keys())

    def _setup_client(self, host, port, password, platform, **kwargs):
        if host and ":" in host:
            spli_ = host.split(":")
            host = spli_[0]
            port = int(spli_[-1])
            if host.startswith("http"):
                logger.error("Your REDIS_URI should not start with http !")
                import sys

                sys.exit()
        elif not host or not port:
            logger.error("Port Number not found")
            import sys

            sys.exit()

        kwargs["host"] = host
        kwargs["password"] = password
        kwargs["port"] = port

        if platform.lower() == "qovery" and not host:
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

        return Redis(**kwargs)
