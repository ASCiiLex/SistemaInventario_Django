from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.http import require_POST

from ..models import UserNotification
from ..utils import send_ui_event_to_all
from .utils import get_filtered_notifications, get_products, has_unread, user_qs


def _render_table(request):
    qs, filters_ctx = get_filtered_notifications(request)

    context = {
        "user_notifications": qs,
        "notifications": [un.notification for un in qs],
        "products": get_products(),
        "has_unread": has_unread(request),
        **filters_ctx,
    }

    response = render(request, "notifications/partials/notifications_table.html", context)
    response["HX-Trigger"] = '{"inventory:notifications_updated": true}'
    return response


def notifications_mark_all_read(request):
    user_qs(request).filter(seen=False).update(seen=True)

    send_ui_event_to_all({
        "type": "notification",
        "message": "Todas las notificaciones marcadas como leídas"
    })

    return _render_table(request)


def notification_mark_read(request, pk):
    un = get_object_or_404(UserNotification, pk=pk, user=request.user)
    un.seen = True
    un.save(update_fields=["seen"])

    send_ui_event_to_all({
        "type": "notification",
        "message": "Notificación marcada como leída"
    })

    return _render_table(request)


def notification_mark_unread(request, pk):
    un = get_object_or_404(UserNotification, pk=pk, user=request.user)
    un.seen = False
    un.save(update_fields=["seen"])

    send_ui_event_to_all({
        "type": "notification",
        "message": "Notificación marcada como no leída"
    })

    return _render_table(request)


def notifications_toggle_all(request):
    qs = user_qs(request)

    if qs.filter(seen=False).exists():
        qs.update(seen=True)
        message = "Todas marcadas como leídas"
    else:
        qs.update(seen=False)
        message = "Todas marcadas como no leídas"

    send_ui_event_to_all({
        "type": "notification",
        "message": message
    })

    if request.headers.get("HX-Request"):
        if "panel" in request.path:
            from .panel import notifications_panel
            return notifications_panel(request)

        return _render_table(request)

    return redirect("notifications_list")


def notifications_counter(request):
    unread = user_qs(request).filter(seen=False).count()

    response = render(
        request,
        "notifications/partials/bell.html",
        {"unread": unread}
    )

    response["HX-Trigger"] = '{"inventory:notifications_updated": true}'
    return response


@require_POST
def notifications_bulk_action(request):
    action = request.POST.get("action")
    ids = request.POST.getlist("selected")

    if not ids:
        return _render_table(request)

    qs = UserNotification.objects.filter(id__in=ids, user=request.user)

    if action == "read":
        qs.update(seen=True)
        message = "Notificaciones marcadas como leídas"

    elif action == "unread":
        qs.update(seen=False)
        message = "Notificaciones marcadas como no leídas"

    elif action == "delete":
        qs.delete()
        message = "Notificaciones eliminadas"

    else:
        return _render_table(request)

    send_ui_event_to_all({
        "type": "notification",
        "message": message
    })

    return _render_table(request)