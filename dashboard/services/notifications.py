from django.db.models import Count
from notifications.models import Notification


def get_notifications_summary():
    return {
        "notifications_total": Notification.objects.count(),
        "notifications_unread": Notification.objects.filter(seen=False).count(),
        "notifications_by_type": Notification.objects.values("type").annotate(total=Count("id")),
    }


def get_recent_notifications(limit=10):
    return Notification.objects.order_by("-created_at")[:limit]