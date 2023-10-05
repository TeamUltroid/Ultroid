from psycopg2 import pool

from .base_db import BaseDatabase

class Database(BaseDatabase):
    '''
    (dbUrl: str) will be something like this - postgres://user:password@host.domain/user
    This is free to get on internet form websites like elephantSQL or cockroachlabs #notSponsored
    '''
    def __init__(self, dbUrl: str, dBname='Ultroid'):
        self.pool = pool.SimpleConnectionPool(1, 3, dsn=dbUrl, sslmode='require')
        self.pool_conn = self.pool.getconn()
        self.pool_cursor = self.pool_conn.cursor()
        self.pool_conn.autocommit = True
        self.pool_cursor.execute("CREATE TABLE IF NOT EXISTS Ultroid (ultroidCli varchar(70))")
        super().__init__()

    def __repr__(self):
        return f"<Ultroid.PostgreSQL\n -total_keys: {len(self.keys())}\n>"

    @property
    def name(self):
        return "postgreSQL"

    @property
    def usage(self):
        self.pool_cursor.execute("SELECT pg_size_pretty(pg_relation_size('Ultroid')) AS size")
        data = self.pool_cursor.fetchall()
        return int(data[0][0].split()[0])

    def keys(self):
        self.pool_cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name  = 'ultroid'")  # case sensitive
        data = self.pool_cursor.fetchall()
        return [_[0] for _ in data]

    def set(self, key, value):
        try:
            self.pool_cursor.execute(f"ALTER TABLE Ultroid DROP COLUMN IF EXISTS {key}")
        except (psycopg2.errors.UndefinedColumn, psycopg2.errors.SyntaxError):
            pass
        except BaseException as er:
            LOGS.exception(er)
        self._cache.update({key: value})
        self.pool_cursor.execute(f"ALTER TABLE Ultroid ADD {key} TEXT")
        self.pool_cursor.execute(f"INSERT INTO Ultroid ({key}) values (%s)", (str(value),))
        return True

    def delete(self, key):
        try:
            self.pool_cursor.execute(f"ALTER TABLE Ultroid DROP COLUMN {key}")
        except psycopg2.errors.UndefinedColumn:
            return False
        return True

    def get(self, key):
        try:
            self.pool_cursor.execute(f"SELECT {variable} FROM Ultroid")
        except psycopg2.errors.UndefinedColumn:
            return None
        data = self.pool_cursor.fetchall()
        if not data:
            return None
        if len(data) >= 1:
            for i in data:
                if i[0]:
                    return i[0]

    def flushall(self):
        self._cache.clear()
        self.pool_cursor.execute("DROP TABLE Ultroid")
        self.pool_cursor.execute("CREATE TABLE IF NOT EXISTS Ultroid (ultroidCli varchar(70))")
        return True
