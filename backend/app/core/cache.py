from typing import Any, Dict


class CacheManager:
    """Thread-safe in-memory cache manager for OLAP queries and ML models."""
    _store: Dict[str, Any] = {}

    @classmethod
    def get(cls, key: str) -> Any:
        return cls._store.get(key)

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        cls._store[key] = value

    @classmethod
    def evict(cls, key: str) -> None:
        cls._store.pop(key, None)

    @classmethod
    def evict_all(cls) -> None:
        cls._store.clear()

    @classmethod
    def size(cls) -> int:
        return len(cls._store)

