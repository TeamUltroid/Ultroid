from localdb import Database as _Database

from .base_db import BaseDatabase

class Database(BaseDatabase):
    def __init__(self, dbname="UltroidDB"):
        self.dB = _Database(database_name=dbname)
        super().__init__()

    def __repr__(self):
        return f"<Ultroid.LocalDB\n -total_keys: {len(self.keys())}\n>"

    @property
    def name(self):
        return "Local"

    @property
    def usage(self):
        return self.dB.size

    def keys(self):
        return self.dB._cache.keys()

    def set(self, key, value):
        return self.dB.set(key, value)

    def delete(self, key):
        return self.dB.delete(key)

    def get(self, key):
        return self.dB.get(key)

    def flushall(self):
        for key in self.keys():
            self.dB.delete(key)
        return True