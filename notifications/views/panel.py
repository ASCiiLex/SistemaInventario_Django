from django.shortcuts import render, get_object_or_404

from ..models import UserNotification
from ..utils import send_ui_event_to_all
from ..constants import Events
from ..services import sync_notifications_for_org
from dashboard.services.notifications import get_grouped_notifications  # 🔥 IMPORTANTE
from .utils import user_qs, has_unread


def notifications_panel(request):
    # 🔥 sincroniza
    sync_notifications_for_org(request.organization)

    grouped = get_grouped_notifications(
        request.user,
        request.organization
    )

    context = {
        "grouped_notifications": grouped,
        "has_unread": has_unread(request),
    }

    return render(request, "notifications/partials/panel.html", context)


def notifications_panel_mark_all(request):
    qs = user_qs(request).filter(notification__is_active=True)

    for un in qs:
        un.notification.is_active = False
        un.notification.save(update_fields=["is_active"])
        un.seen = True
        un.save(update_fields=["seen"])

    send_ui_event_to_all({"event": Events.NOTIFICATIONS_UPDATED})

    return notifications_panel(request)


def notifications_panel_mark_one(request, pk):
    un = get_object_or_404(UserNotification, pk=pk, user=request.user)

    notification = un.notification
    notification.is_active = False
    notification.save(update_fields=["is_active"])

    un.seen = True
    un.save(update_fields=["seen"])

    send_ui_event_to_all({"event": Events.NOTIFICATIONS_UPDATED})

    return notifications_panel(request)


def notifications_panel_mark_unread(request, pk):
    un = get_object_or_404(UserNotification, pk=pk, user=request.user)

    un.seen = False
    un.save(update_fields=["seen"])

    send_ui_event_to_all({"event": Events.NOTIFICATIONS_UPDATED})

    return notifications_panel(request)