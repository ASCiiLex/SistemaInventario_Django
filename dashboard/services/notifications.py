from django.db.models import Count
from notifications.models import Notification


def get_notifications_summary():
    qs = Notification.objects.all()

    return {
        "notifications_total": qs.count(),
        "notifications_unread": qs.filter(seen=False).count(),
        "notifications_by_type": qs.values("type").annotate(total=Count("id")),
    }


def get_recent_notifications(limit=10):
    return Notification.objects.select_related("product").order_by("-created_at")[:limit]