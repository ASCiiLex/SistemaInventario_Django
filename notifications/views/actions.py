from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.http import require_POST

from ..models import Notification
from .utils import get_filtered_notifications, get_products


def _render_table(request):
    notifications, filters_ctx = get_filtered_notifications(request)

    context = {
        "notifications": notifications,
        "products": get_products(),
        "has_unread": Notification.objects.filter(seen=False).exists(),
        **filters_ctx,
    }

    response = render(request, "notifications/partials/notifications_table.html", context)
    response["HX-Trigger"] = '{"inventory:notifications_updated": true}'
    return response


def notifications_mark_all_read(request):
    Notification.objects.filter(seen=False).update(seen=True)
    return _render_table(request)


def notification_mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk)
    n.seen = True
    n.save()
    return _render_table(request)


def notification_mark_unread(request, pk):
    n = get_object_or_404(Notification, pk=pk)
    n.seen = False
    n.save()
    return _render_table(request)


def notifications_toggle_all(request):
    has_unread = Notification.objects.filter(seen=False).exists()

    if has_unread:
        Notification.objects.filter(seen=False).update(seen=True)
    else:
        Notification.objects.update(seen=False)

    if request.headers.get("HX-Request"):
        if "panel" in request.path:
            from .panel import notifications_panel
            return notifications_panel(request)

        return _render_table(request)

    return redirect("notifications_list")


def notifications_counter(request):
    unread = Notification.objects.filter(seen=False).count()

    response = render(
        request,
        "notifications/partials/bell.html",
        {"unread": unread}
    )

    response["HX-Trigger"] = '{"inventory:notifications_updated": true}'
    return response


# ================================
# BULK ACTIONS
# ================================

@require_POST
def notifications_bulk_action(request):
    action = request.POST.get("action")
    ids = request.POST.getlist("selected")

    if not ids:
        return _render_table(request)

    qs = Notification.objects.filter(id__in=ids)

    if action == "read":
        qs.update(seen=True)

    elif action == "unread":
        qs.update(seen=False)

    else:
        return _render_table(request)

    return _render_table(request)

