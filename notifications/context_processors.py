from django.core.cache import cache
from django.conf import settings
from notifications.models import UserNotification


def notifications_unread(request):
    if not request.user.is_authenticated:
        return {"notifications_unread": 0}

    org_id = getattr(request, "organization", None)
    org_id = org_id.id if org_id else "none"

    cache_key = f"notifications:unread_count:{request.user.id}:{org_id}"

    cached = cache.get(cache_key)
    if cached is not None:
        return {"notifications_unread": cached}

    count = UserNotification.objects.filter(
        user=request.user,
        seen=False,
        notification__organization=request.organization
    ).count()

    cache.set(cache_key, count, settings.CACHE_TTL["notifications"])

    return {"notifications_unread": count}