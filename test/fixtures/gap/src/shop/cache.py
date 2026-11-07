_CACHE: dict[str, object] = {}


def get(key: str) -> object | None:
    return _CACHE.get(key)


def put(key: str, value: object) -> None:
    _CACHE[key] = value
