import time
from django.core.cache import cache


class RateLimiter:

    def __init__(self, key_prefix, limit, window):
        self.key_prefix = key_prefix
        self.limit = limit
        self.window = window  # segundos

    def is_allowed(self, identifier):
        now = int(time.time())
        window_start = now - self.window

        key = f"rl:{self.key_prefix}:{identifier}"

        requests = cache.get(key, [])

        # limpiar requests fuera de ventana
        requests = [ts for ts in requests if ts > window_start]

        if len(requests) >= self.limit:
            return False

        requests.append(now)
        cache.set(key, requests, self.window)

        return True