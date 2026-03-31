from django.shortcuts import render
from django.utils.timezone import localdate
from django.db.models import Count
from datetime import timedelta

from .utils import user_qs


def notifications_summary(request):
    qs = user_qs(request)

    return render(request, "dashboard/partials/notifications_summary.html", {
        "total_notifications": qs.count(),
        "unread_notifications": qs.filter(seen=False).count(),
        "by_type": qs.values("notification__type").annotate(c=Count("id")),
    })


def notifications_chart(request):
    today = localdate()
    start = today - timedelta(days=29)

    qs = (
        user_qs(request)
        .filter(notification__created_at__date__gte=start)
        .extra(select={"day": "date(notification.created_at)"})
        .values("day")
        .annotate(c=Count("id"))
        .order_by("day")
    )

    return render(request, "dashboard/partials/notifications_chart.html", {
        "labels": [row["day"].strftime("%d/%m") for row in qs],
        "values": [row["c"] for row in qs],
    })


def notifications_recent(request):
    qs = user_qs(request).order_by("-notification__created_at")[:20]

    return render(
        request,
        "dashboard/partials/notifications_recent.html",
        {"notifications": [un.notification for un in qs]},
    )