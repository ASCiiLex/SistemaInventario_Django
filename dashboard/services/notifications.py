from django.db.models import Count
from notifications.models import Notification


def get_notifications_summary():
    qs = Notification.objects.all()

    # 🔥 Agrupación limpia + labels humanos
    by_type_raw = qs.values("type").annotate(total=Count("id"))

    by_type = []
    for item in by_type_raw:
        type_key = item["type"]
        label = dict(Notification.TYPE_CHOICES).get(type_key, type_key)

        by_type.append({
            "type": type_key,
            "label": label,
            "total": item["total"],
        })

    return {
        "notifications_total": qs.count(),
        "notifications_unread": qs.filter(seen=False).count(),
        "notifications_by_type": by_type,
    }


def get_recent_notifications(limit=10):
    return (
        Notification.objects
        .select_related("product", "location")
        .order_by("-created_at")[:limit]
    )