# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import time
from typing import Dict, Any, Optional
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if key not in self._cache:
                return None
            entry = self._cache[key]
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                return None

            return entry["data"]

    def set(self, key: str, value: Dict[str, Any]) -> None:
        with self._lock:
            self._cache[key] = {"data": value, "expires_at": time.time() + self.ttl}

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


# Global cache instance with 5 minute TTL
owner_cache = TTLCache(ttl_seconds=300)
