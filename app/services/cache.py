import time

_cache: dict[str, dict] = {}


def get_cache(key: str) -> dict | None:
    if key not in _cache:
        return None

    entry = _cache[key]
    if time.time() - entry["timestamp"] > entry["ttl"]:
        del _cache[key]
        return None

    return entry["data"]


def set_cache(key: str, data: dict, ttl: int) -> None:
    _cache[key] = {"data": data, "timestamp": time.time(), "ttl": ttl}


def clear_cache() -> None:
    _cache.clear()


def cache_stats() -> dict:
    now = time.time()
    return {
        "size": len(_cache),
        "entries": [
            {
                "key": key,
                "ttl_remaining": round(entry["ttl"] - (now - entry["timestamp"]), 1),
            }
            for key, entry in _cache.items()
        ],
    }
