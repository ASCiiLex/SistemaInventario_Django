from django.shortcuts import render
from dashboard.services.notifications import (
    get_recent_notifications,
    get_notifications_summary,
)


def dashboard_notifications_recent(request):
    if not request.organization:
        return render(request, "dashboard/partials/notifications_recent.html", {"notifications": []})

    notifications = get_recent_notifications(
        request.user,
        request.organization
    )

    return render(
        request,
        "dashboard/partials/notifications_recent.html",
        {"notifications": notifications},
    )


def dashboard_notifications_summary(request):
    if not request.organization:
        return render(request, "dashboard/partials/notifications_summary.html", {})

    context = get_notifications_summary(
        request.user,
        request.organization
    )

    return render(
        request,
        "dashboard/partials/notifications_summary.html",
        context,
    )