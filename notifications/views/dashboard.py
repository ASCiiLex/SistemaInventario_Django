from django.shortcuts import render
from django.utils.timezone import localdate
from django.db.models import Count
from datetime import timedelta

from ..models import Notification


def notifications_summary(request):
    return render(request, "dashboard/partials/notifications_summary.html", {
        "total_notifications": Notification.objects.count(),
        "unread_notifications": Notification.objects.filter(seen=False).count(),
        "by_type": Notification.objects.values("type").annotate(c=Count("id")),
    })


def notifications_chart(request):
    today = localdate()
    start = today - timedelta(days=29)

    qs = (
        Notification.objects.filter(created_at__date__gte=start)
        .extra(select={"day": "date(created_at)"})
        .values("day")
        .annotate(c=Count("id"))
        .order_by("day")
    )

    return render(request, "dashboard/partials/notifications_chart.html", {
        "labels": [row["day"].strftime("%d/%m") for row in qs],
        "values": [row["c"] for row in qs],
    })


def notifications_recent(request):
    return render(
        request,
        "dashboard/partials/notifications_recent.html",
        {"notifications": Notification.objects.select_related("product").order_by("-created_at")[:20]},
    )
