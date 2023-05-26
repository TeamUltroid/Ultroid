from ast import literal_eval
from collections import deque
from contextlib import suppress

from core.config import Var


class BaseDatabase:
    def __init__(self, *args, **kwargs):
        self._cache = {}
        self._handlers = {}

    def get(self, key):
        ...

    def set(self, key, value):
        ...

    def delete(self, key):
        ...

    @property
    def name(self):
        return "database"

    @property
    def usage(self):
        return 0

    def keys(self):
        return []

    def get_config(self, key):
        return getattr(Var, key) or self.get_key(key)

    def get_key(self, key):
        if key in self._cache:
            return self._cache[key]
        value = self._get_data(key)
        self._cache.update({key: value})
        return value

    def re_cache(self):
        self._cache.clear()
        for key in self.keys():
            self._cache.update({key: self.get_key(key)})

    def del_key(self, key):
        if key in self._cache:
            del self._cache[key]
        self.delete(key)
        with suppress(KeyError):
            handler, arg, kwargs = self._handlers[key]["delete"]
            handler(*arg, **kwargs)
        return True

    def _get_data(self, key=None, data=None):
        if key:
            data = self.get(str(key))
        if data and isinstance(data, str):
            with suppress(BaseException):
                data = literal_eval(data)
        return data

    def on(self, key, method, handler, *args, **kwargs):
        if not self._handlers.get(key):
            self._handlers[key] = {}
        self._handlers[key][method] = (handler, args, kwargs)

    def set_key(self, key, value):
        value = self._get_data(data=value)
        self._cache[key] = value
        with suppress(KeyError):
            handler, arg, kwargs = self._handlers[key]["change"]
            handler(key, value, self.get_key(key), *arg, **kwargs)
        return self.set(str(key), str(value))

    def rename(self, key1, key2):
        if _ := self.get_key(key1):
            self.del_key(key1)
            self.set_key(key2, _)
            return 0
        return 1

    def cflush(self):
        deque(
            map(
                lambda key: self.del_key(key),
                filter(lambda x: not x.startswith("_"), self.keys()),
            ),
            0,
        )
