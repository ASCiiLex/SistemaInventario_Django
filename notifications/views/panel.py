from django.shortcuts import render, get_object_or_404
from ..models import Notification
from .utils import group_notifications_by_product


def _get_panel_notifications(request):
    q = request.GET.get("q", "").strip().lower()

    qs = Notification.objects.select_related("product").order_by("-created_at")

    if q:
        qs = qs.filter(message__icontains=q)

    return qs


def _panel_context(notifications):
    return {
        "grouped_notifications": group_notifications_by_product(notifications),
        "has_unread": Notification.objects.filter(seen=False).exists(),
    }


def notifications_panel(request):
    notifications = _get_panel_notifications(request)
    context = _panel_context(notifications)
    return render(request, "notifications/partials/panel.html", context)


def notifications_panel_mark_all(request):
    Notification.objects.filter(seen=False).update(seen=True)
    return notifications_panel(request)


def notifications_panel_mark_one(request, pk):
    n = get_object_or_404(Notification, pk=pk)
    n.seen = True
    n.save()
    return notifications_panel(request)


def notifications_panel_mark_unread(request, pk):
    n = get_object_or_404(Notification, pk=pk)
    n.seen = False
    n.save()
    return notifications_panel(request)
