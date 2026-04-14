from django.core.cache import cache
import logging

logger = logging.getLogger("inventory.metrics")


class SafeCache:

    MAX_KEYS = 10000  # límite de seguridad

    @staticmethod
    def get_cache_size():
        try:
            client = cache._cache.get_client()
            return client.dbsize()
        except Exception:
            return 0

    @classmethod
    def enforce_limits(cls):
        size = cls.get_cache_size()

        if size > cls.MAX_KEYS:
            logger.warning("cache.limit.exceeded", extra={
                "current_size": size,
                "max_size": cls.MAX_KEYS
            })

            # 🔥 estrategia simple: flush controlado
            try:
                cache.clear()
                logger.warning("cache.flushed")
            except Exception:
                logger.error("cache.flush.failed")