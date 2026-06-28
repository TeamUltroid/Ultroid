# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import ast
import os
from typing import Any, Iterable, Optional

from .. import run_as_module
from . import *  # noqa: F401,F403

if run_as_module:
    from ..configs import Var

# Each backend is imported lazily so missing optional deps don't blow up
# startup before we even know which DB the user picked.
Redis = MongoClient = psycopg2 = LocalDatabase = None
if Var.REDIS_URI or Var.REDISHOST:
    try:
        from redis import Redis  # type: ignore[assignment]
    except ImportError as err:  # pragma: no cover - clearer error than os.system
        LOGS.critical(  # noqa: F405
            "REDIS_URI is configured but the 'redis' package is not installed. "
            "Run: pip install -U redis hiredis"
        )
        raise SystemExit(1) from err
elif Var.MONGO_URI:
    try:
        from pymongo import MongoClient  # type: ignore[assignment]
    except ImportError as err:  # pragma: no cover
        LOGS.critical(  # noqa: F405
            "MONGO_URI is configured but the 'pymongo' package is not installed. "
            "Run: pip install -U 'pymongo[srv]'"
        )
        raise SystemExit(1) from err
elif Var.DATABASE_URL:
    try:
        import psycopg2  # type: ignore[assignment]
        from psycopg2 import sql as _pgsql  # type: ignore[assignment]
    except ImportError as err:  # pragma: no cover
        LOGS.critical(  # noqa: F405
            "DATABASE_URL is configured but 'psycopg2' is not installed. "
            "Run: pip install -U psycopg2-binary"
        )
        raise SystemExit(1) from err
else:
    try:
        from localdb import Database as LocalDatabase  # type: ignore[assignment]
    except ImportError as err:  # pragma: no cover
        LOGS.critical(  # noqa: F405
            "No database backend is configured. Either set REDIS_URI / MONGO_URI / "
            "DATABASE_URL, or install 'localdb.json' for a file-backed fallback."
        )
        raise SystemExit(1) from err

# ---------------------------------------------------------------------------


class _BaseDatabase:
    """Common cache + (de)serialisation logic shared by every backend."""

    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}

    # ------------------------ helpers --------------------------------
    def _get_data(self, key: Optional[str] = None, data: Any = None) -> Any:
        if key is not None:
            data = self.get(str(key))  # type: ignore[attr-defined]
        if isinstance(data, str):
            try:
                data = ast.literal_eval(data)
            except (SyntaxError, ValueError):
                pass
        return data

    # ------------------------ public API -----------------------------
    def get_key(self, key: str) -> Any:
        if key in self._cache:
            return self._cache[key]
        value = self._get_data(key)
        self._cache[key] = value
        return value

    def set_key(self, key: str, value: Any, cache_only: bool = False) -> Any:
        value = self._get_data(data=value)
        self._cache[key] = value
        if cache_only:
            return None
        return self.set(str(key), str(value))  # type: ignore[attr-defined]

    def del_key(self, key: str) -> bool:
        self._cache.pop(key, None)
        self.delete(key)  # type: ignore[attr-defined]
        return True

    def re_cache(self) -> None:
        self._cache.clear()
        for key in self.keys():  # type: ignore[attr-defined]
            self._cache[key] = self.get_key(key)

    def rename(self, key1: str, key2: str) -> int:
        value = self.get_key(key1)
        if value:
            self.del_key(key1)
            self.set_key(key2, value)
            return 0
        return 1

    def ping(self) -> int:
        return 1

    def keys(self) -> Iterable[str]:
        return []

    @property
    def usage(self) -> int:
        return 0


# ----------------------------- Mongo -----------------------------------


class MongoDB(_BaseDatabase):
    def __init__(self, key, dbname: str = "UltroidDB"):
        self.dB = MongoClient(key, serverSelectionTimeoutMS=5000)
        self.db = self.dB[dbname]
        super().__init__()

    def __repr__(self) -> str:
        return f"<Ultroid.MongoDB total_keys={len(list(self.keys()))}>"

    @property
    def name(self) -> str:
        return "Mongo"

    @property
    def usage(self) -> int:
        return self.db.command("dbstats")["dataSize"]

    def ping(self) -> bool:
        return bool(self.dB.server_info())

    def keys(self):
        return self.db.list_collection_names()

    def set(self, key: str, value: Any) -> bool:
        if key in self.keys():
            self.db[key].replace_one({"_id": key}, {"value": str(value)})
        else:
            self.db[key].insert_one({"_id": key, "value": str(value)})
        return True

    def delete(self, key: str) -> None:
        self.db.drop_collection(key)

    def get(self, key: str) -> Any:
        doc = self.db[key].find_one({"_id": key})
        return doc["value"] if doc else None

    def flushall(self) -> bool:
        self.dB.drop_database("UltroidDB")
        self._cache.clear()
        return True


# ------------------------------ SQL ------------------------------------
#
# Thanks to "Akash Pattnaik" / @BLUE-DEVIL1134 for the original SQL impl.
# This rewrite uses ``psycopg2.sql`` composition everywhere so column names
# (which are derived from arbitrary user-controlled DB keys) can no longer
# be used as a SQL-injection vector.
# https://www.psycopg.org/docs/sql.html


class SqlDB(_BaseDatabase):
    _TABLE = "ultroid"

    def __init__(self, url: str) -> None:
        self._url = url
        self._connection = None
        self._cursor = None
        try:
            self._connection = psycopg2.connect(dsn=url)
            self._connection.autocommit = True
            self._cursor = self._connection.cursor()
            self._cursor.execute(
                _pgsql.SQL(
                    "CREATE TABLE IF NOT EXISTS {tbl} (ultroidCli varchar(70))"
                ).format(tbl=_pgsql.Identifier(self._TABLE))
            )
        except Exception as err:
            LOGS.exception(err)  # noqa: F405
            LOGS.critical("Invalid SQL database, exiting.")  # noqa: F405
            if self._connection:
                self._connection.close()
            raise SystemExit(1) from err
        super().__init__()

    @property
    def name(self) -> str:
        return "SQL"

    @property
    def usage(self) -> int:
        self._cursor.execute(
            _pgsql.SQL(
                "SELECT pg_size_pretty(pg_relation_size({tbl})) AS size"
            ).format(tbl=_pgsql.Literal(self._TABLE))
        )
        data = self._cursor.fetchall()
        return int(data[0][0].split()[0])

    def keys(self):
        self._cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = %s",
            (self._TABLE,),
        )
        return [row[0] for row in self._cursor.fetchall()]

    def get(self, variable: str) -> Any:
        try:
            self._cursor.execute(
                _pgsql.SQL("SELECT {col} FROM {tbl}").format(
                    col=_pgsql.Identifier(variable),
                    tbl=_pgsql.Identifier(self._TABLE),
                )
            )
        except psycopg2.errors.UndefinedColumn:
            return None
        for row in self._cursor.fetchall():
            if row[0]:
                return row[0]
        return None

    def set(self, key: str, value: Any) -> bool:
        try:
            self._cursor.execute(
                _pgsql.SQL("ALTER TABLE {tbl} DROP COLUMN IF EXISTS {col}").format(
                    tbl=_pgsql.Identifier(self._TABLE),
                    col=_pgsql.Identifier(key),
                )
            )
        except (psycopg2.errors.UndefinedColumn, psycopg2.errors.SyntaxError):
            pass
        except Exception as err:  # pragma: no cover - defensive
            LOGS.exception(err)  # noqa: F405
        self._cache[key] = value
        self._cursor.execute(
            _pgsql.SQL("ALTER TABLE {tbl} ADD {col} TEXT").format(
                tbl=_pgsql.Identifier(self._TABLE), col=_pgsql.Identifier(key)
            )
        )
        self._cursor.execute(
            _pgsql.SQL("INSERT INTO {tbl} ({col}) VALUES (%s)").format(
                tbl=_pgsql.Identifier(self._TABLE), col=_pgsql.Identifier(key)
            ),
            (str(value),),
        )
        return True

    def delete(self, key: str) -> bool:
        try:
            self._cursor.execute(
                _pgsql.SQL("ALTER TABLE {tbl} DROP COLUMN {col}").format(
                    tbl=_pgsql.Identifier(self._TABLE), col=_pgsql.Identifier(key)
                )
            )
        except psycopg2.errors.UndefinedColumn:
            return False
        return True

    def flushall(self) -> bool:
        self._cache.clear()
        self._cursor.execute(
            _pgsql.SQL("DROP TABLE {tbl}").format(tbl=_pgsql.Identifier(self._TABLE))
        )
        self._cursor.execute(
            _pgsql.SQL(
                "CREATE TABLE IF NOT EXISTS {tbl} (ultroidCli varchar(70))"
            ).format(tbl=_pgsql.Identifier(self._TABLE))
        )
        return True


# ----------------------------- Redis -----------------------------------


class RedisDB(_BaseDatabase):
    def __init__(
        self,
        host: Optional[str],
        port: Optional[int],
        password: Optional[str],
        platform: str = "",
        logger=None,
        *args,
        **kwargs,
    ) -> None:
        logger = logger or LOGS  # noqa: F405
        if host and ":" in host:
            head, _, tail = host.rpartition(":")
            host = head
            try:
                port = int(tail)
            except ValueError:
                logger.error("Invalid Redis port number in REDIS_URI.")
                raise SystemExit(1)
            if host.startswith("http"):
                logger.error("REDIS_URI should not start with http(s)://")
                raise SystemExit(1)
        elif not host or not port:
            logger.error("Redis host / port not configured properly.")
            raise SystemExit(1)

        kwargs.update({"host": host, "password": password, "port": port})

        if platform.lower() == "qovery" and not host:
            for env_name in os.environ:
                if env_name.startswith("QOVERY_REDIS_") and env_name.endswith("_HOST"):
                    hash_ = env_name.split("_", maxsplit=2)[1].split("_")[0]
                    kwargs["host"] = os.environ.get(f"QOVERY_REDIS_{hash_}_HOST")
                    kwargs["port"] = os.environ.get(f"QOVERY_REDIS_{hash_}_PORT")
                    kwargs["password"] = os.environ.get(
                        f"QOVERY_REDIS_{hash_}_PASSWORD"
                    )
                    break

        self.db = Redis(**kwargs)
        # Delegate basic ops directly to the redis client – the fast path.
        self.set = self.db.set
        self.get = self.db.get
        self.keys = self.db.keys
        self.delete = self.db.delete
        super().__init__()

    @property
    def name(self) -> str:
        return "Redis"

    @property
    def usage(self) -> int:
        return sum(self.db.memory_usage(x) for x in self.keys())


# ----------------------------- LocalDB ---------------------------------


class LocalDB(_BaseDatabase):
    def __init__(self) -> None:
        self.db = LocalDatabase("ultroid")
        self.get = self.db.get
        self.set = self.db.set
        self.delete = self.db.delete
        super().__init__()

    @property
    def name(self) -> str:
        return "LocalDB"

    def keys(self):
        return self._cache.keys()

    def __repr__(self) -> str:
        return f"<Ultroid.LocalDB total_keys={len(self._cache)}>"


# ---------------------------------------------------------------------------


def UltroidDB():
    """Return the configured database backend, exiting if none is usable."""
    from .. import HOSTED_ON

    try:
        if Redis:
            return RedisDB(
                host=Var.REDIS_URI or Var.REDISHOST,
                password=Var.REDIS_PASSWORD or Var.REDISPASSWORD,
                port=Var.REDISPORT,
                platform=HOSTED_ON,
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True,
            )
        if MongoClient:
            return MongoDB(Var.MONGO_URI)
        if psycopg2:
            return SqlDB(Var.DATABASE_URL)
        LOGS.critical(  # noqa: F405
            "No remote DB available – falling back to LocalDB. "
            "For production, install redis / pymongo / psycopg2-binary."
        )
        return LocalDB()
    except SystemExit:
        raise
    except Exception as err:
        LOGS.exception(err)  # noqa: F405
        raise SystemExit(1) from err
