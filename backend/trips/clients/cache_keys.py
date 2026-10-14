from hashlib import sha256


def cache_key(namespace, *parts):
    digest = sha256("|".join(str(part) for part in parts).encode()).hexdigest()
    return f"{namespace}:{digest}"
