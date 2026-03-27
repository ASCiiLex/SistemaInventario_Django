from django.shortcuts import render
from dashboard.services.notifications import get_recent_notifications


def dashboard_notifications_recent(request):
    notifications = get_recent_notifications()
    return render(
        request,
        "dashboard/partials/notifications_recent.html",
        {"notifications": notifications},
    )