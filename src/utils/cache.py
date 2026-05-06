import asyncio
from datetime import datetime
from typing import Any

from pytz import UTC


class TTLCache:
    def __init__(self, default_ttl: int = 300):
        self._cache: dict[str, dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def set(self, key: str, value: Any, ttl: int | None = None):
        """Set a value in the cache with an optional specific TTL."""
        expiry = datetime.now(UTC).timestamp() + (ttl or self.default_ttl)
        self._cache[key] = {"value": value, "expiry": expiry}

    def get(self, key: str) -> Any | None:
        """Get a value if it hasn't expired; otherwise, remove it and return None."""
        item = self._cache.get(key)

        if not item:
            return None

        if datetime.now(UTC).timestamp() > item["expiry"]:
            del self._cache[key]
            return None

        return item["value"]

    def delete(self, key: str):
        """Manually remove a key."""
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """Wipe the entire cache."""
        self._cache.clear()


class AsyncTTLCache:
    def __init__(self, default_ttl: int = 300):
        self._cache: dict[str, dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()

    async def set(self, key: str, value: Any, ttl: int | None = None):
        async with self._lock:
            expiry = datetime.now(UTC).timestamp() + (ttl or self.default_ttl)
            self._cache[key] = {"value": value, "expiry": expiry}

    async def get(self, key: str) -> Any | None:
        async with self._lock:
            item = self._cache.get(key)
            if not item:
                return None

            if datetime.now(UTC).timestamp() > item["expiry"]:
                del self._cache[key]
                return None

            return item["value"]

    async def delete(self, key: str):
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self):
        async with self._lock:
            self._cache.clear()
