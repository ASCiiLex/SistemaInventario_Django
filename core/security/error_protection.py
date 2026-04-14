import time
import hashlib
from django.core.cache import cache


class ErrorProtector:

    def __init__(self, window=10, limit=5):
        self.window = window
        self.limit = limit

    def should_log(self, error_type: str, context: str = ""):
        now = int(time.time())
        window_start = now - self.window

        signature = self._build_signature(error_type, context)
        key = f"err:{signature}"

        events = cache.get(key, [])

        # limpiar antiguos
        events = [ts for ts in events if ts > window_start]

        if len(events) >= self.limit:
            return False

        events.append(now)
        cache.set(key, events, self.window)

        return True

    def _build_signature(self, error_type, context):
        raw = f"{error_type}:{context}"
        return hashlib.md5(raw.encode()).hexdigest()