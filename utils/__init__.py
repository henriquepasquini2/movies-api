import hashlib
import json
from typing import Any


def generate_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """
    Generate a unique cache key.

    :param prefix: A string prefix to identify the context (e.g., method name).
    :param args: Positional arguments for the method.
    :param kwargs: Keyword arguments for the method.
    :return: A unique cache key string.
    """
    # Serialize args and kwargs to a JSON-like string
    key_data = {"args": args, "kwargs": kwargs}

    # Ensure deterministic ordering for kwargs
    serialized = json.dumps(key_data, sort_keys=True, default=str)

    # Hash the serialized data for a compact and unique key
    hash_digest = hashlib.md5(serialized.encode()).hexdigest()

    # Combine the prefix and hash to form the final key
    return f"{prefix}:{hash_digest}"
