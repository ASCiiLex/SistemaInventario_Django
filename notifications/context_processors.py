from django.core.cache import cache
from django.conf import settings
from notifications.models import UserNotification


def notifications_unread(request):
    cache_key = "notifications:unread_count"

    cached = cache.get(cache_key)
    if cached is not None:
        return {"notifications_unread": cached}

    count = UserNotification.objects.filter(seen=False).count()

    cache.set(cache_key, count, settings.CACHE_TTL["notifications"])

    return {"notifications_unread": count}