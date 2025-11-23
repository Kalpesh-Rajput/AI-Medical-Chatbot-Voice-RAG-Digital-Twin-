import time
from collections import OrderedDict
from typing import Any, Optional, Tuple
# LRU: Least Recently Used
# TTL: Time To Live (expiry time)

class LRUCacheTTL:
    """
    Simple LRU cache with TTL per entry.
    - capacity: max number of entries
    - default_ttl: seconds before an entry expires
    """

    def __init__(self, capacity: int = 256, default_ttl: int = 3600):
        self.capacity = capacity
        self.default_ttl = default_ttl
        self._store = OrderedDict()  # key -> (value, expiry_ts)

    def _is_expired(self, expiry_ts: float) -> bool:
        return time.time() >= expiry_ts

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if item is None:
            return None
        value, expiry_ts = item
        if self._is_expired(expiry_ts):
            # expired — remove and return None
            del self._store[key]
            return None
        # move to end = most recently used
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if ttl is None:
            ttl = self.default_ttl
        expiry_ts = time.time() + ttl
        if key in self._store:
            del self._store[key]
        elif len(self._store) >= self.capacity:
            # evict least recently used
            self._store.popitem(last=False)
        self._store[key] = (value, expiry_ts)

    def clear(self) -> None:
        self._store.clear()

    def info(self) -> Tuple[int, int]:
        """Return (current_size, capacity)"""
        return len(self._store), self.capacity
