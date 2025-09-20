from __future__ import annotations

import json
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")
_sentry = object()


@dataclass
class PistonyCache:
    cache_hits: int = 0
    cache_misses: int = 0
    cache_loads: int = 0
    cache_removed: int = 0


def _time_now() -> float:
    return time.monotonic()


def default_key_builder(
        objct
) -> str:
    try:
        return json.dumps(
            objct,
            sort_keys=True,
            separators=(",", ":"),
            default=str
        )
    except TypeError:
        return str(objct)


class PistonyCacher(Generic[K, V]):
    def __init__(
        self,
        default_ttl: float = 350.0,
        max_size: int = 1024,
        swr: bool = False,
        cacher_key_builder: Callable[[Any], str] = default_key_builder,
        negative_caching: bool = True,
    ) -> None:
        self._ttl = float(default_ttl)
        self._maxsize = int(max_size)
        self._swr = bool(swr)
        self._cacher_key_builder = cacher_key_builder
        self._negative_caching = negative_caching
        self._store_cache: OrderedDict[
            K,
            tuple[float, float, Any]
        ] = OrderedDict()
        self._threadlock = threading.RLock()
        self._key_locks: dict[K, threading.Lock] = {}
        self.cache_stats = PistonyCache

    def __len__(self) -> int:
        with self._threadlock:
            return len(self._store_cache)

    def __contains__(self, key: K) -> bool:
        return self.fetch_fresh_cache(key) is not None

    def clear_cache(self) -> None:
        with self._threadlock:
            self._store_cache.clear()
            self._key_locks.clear()

    def delete_cache(self, data_key: K) -> None:
        with self._threadlock:
            if data_key in self._store_cache:
                del self._store_cache[data_key]

    def set_cache(
        self,
        key: K,
        value: V | None,
        cache_ttl: float | None = None
    ) -> None:
        pass
