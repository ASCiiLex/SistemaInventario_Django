from django.shortcuts import render, get_object_or_404

from ..models import UserNotification
from ..utils import send_ui_event_to_all
from .utils import group_notifications_by_product, user_qs, has_unread


def _get_panel_notifications(request):
    qs = user_qs(request)

    q = request.GET.get("q", "").strip()

    if q:
        qs = qs.filter(notification__message__icontains=q)

    return qs.order_by("-notification__created_at")


def _panel_context(request, qs):
    return {
        "grouped_notifications": group_notifications_by_product(qs),
        "has_unread": has_unread(request),
    }


def notifications_panel(request):
    qs = _get_panel_notifications(request)
    return render(request, "notifications/partials/panel.html", _panel_context(request, qs))


def notifications_panel_mark_all(request):
    user_qs(request).filter(seen=False).update(seen=True)

    send_ui_event_to_all({
        "type": "notification",
        "message": "Todas las notificaciones marcadas como leídas"
    })

    return notifications_panel(request)


def notifications_panel_mark_one(request, pk):
    un = get_object_or_404(UserNotification, pk=pk, user=request.user)
    un.seen = True
    un.save(update_fields=["seen"])

    send_ui_event_to_all({
        "type": "notification",
        "message": "Notificación marcada como leída"
    })

    return notifications_panel(request)


def notifications_panel_mark_unread(request, pk):
    un = get_object_or_404(UserNotification, pk=pk, user=request.user)
    un.seen = False
    un.save(update_fields=["seen"])

    send_ui_event_to_all({
        "type": "notification",
        "message": "Notificación marcada como no leída"
    })

    return notifications_panel(request)