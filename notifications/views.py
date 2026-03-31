from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import localdate
from django.views.decorators.http import require_POST
from django.db.models import Count
from datetime import timedelta

from .models import Notification, UserNotification
from .utils import send_ui_event_to_all

from products.models import Product


# ================================
# HELPERS
# ================================

def _user_qs(request):
    return UserNotification.objects.filter(user=request.user).select_related(
        "notification__product",
        "notification__location"
    )


def _has_unread(request):
    return _user_qs(request).filter(seen=False).exists()


def _base_context(request, qs, extra=None):
    context = {
        "user_notifications": qs,
        "notifications": [un.notification for un in qs],
        "products": _get_products(),
        "has_unread": _has_unread(request),
    }
    if extra:
        context.update(extra)
    return context


# ================================
# LISTA PRINCIPAL (TABLA)
# ================================

def _get_filtered_notifications(request):
    qs = _user_qs(request)

    status = request.GET.get("status", "")
    product_id = request.GET.get("product", "")
    type_filter = request.GET.get("type", "")
    priority = request.GET.get("priority", "")

    sort = request.GET.get("sort", "created_at")
    direction = request.GET.get("dir", "desc")

    if status == "new":
        qs = qs.filter(seen=False)
    elif status == "read":
        qs = qs.filter(seen=True)

    if product_id:
        qs = qs.filter(notification__product_id=product_id)

    if type_filter:
        qs = qs.filter(notification__type=type_filter)

    if priority:
        qs = qs.filter(notification__priority=priority)

    order = f"-notification__{sort}" if direction == "desc" else f"notification__{sort}"
    qs = qs.order_by(order)

    return qs, {
        "status": status,
        "product_id": product_id,
        "type": type_filter,
        "priority": priority,
        "current_sort": sort,
        "current_dir": direction,
    }


def _get_products():
    import re

    products_qs = Product.objects.all().values("id", "name")

    def natural_key(item):
        return [
            int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', item["name"])
        ]

    return [(p["id"], p["name"]) for p in sorted(products_qs, key=natural_key)]


def notifications_list(request):
    qs, filters_ctx = _get_filtered_notifications(request)
    context = _base_context(request, qs, filters_ctx)

    if request.headers.get("HX-Request"):
        return render(request, "notifications/partials/notifications_table.html", context)

    return render(request, "notifications/list.html", context)


# ================================
# ACCIONES TABLA
# ================================

def notifications_mark_all_read(request):
    _user_qs(request).filter(seen=False).update(seen=True)

    send_ui_event_to_all({
        "type": "notification",
        "message": "Todas las notificaciones marcadas como leídas"
    })

    return notifications_list(request)


def notification_mark_read(request, pk):
    un = get_object_or_404(UserNotification, pk=pk, user=request.user)
    un.seen = True
    un.save(update_fields=["seen"])

    send_ui_event_to_all({
        "type": "notification",
        "message": "Notificación marcada como leída"
    })

    return notifications_list(request)


def notification_mark_unread(request, pk):
    un = get_object_or_404(UserNotification, pk=pk, user=request.user)
    un.seen = False
    un.save(update_fields=["seen"])

    send_ui_event_to_all({
        "type": "notification",
        "message": "Notificación marcada como no leída"
    })

    return notifications_list(request)


# ================================
# CONTADOR NAVBAR
# ================================

def notifications_counter(request):
    unread = _user_qs(request).filter(seen=False).count()

    response = render(
        request,
        "notifications/partials/bell.html",
        {"unread": unread}
    )

    response["HX-Trigger"] = '{"inventory:notifications_updated": true}'
    return response


# ================================
# PANEL LATERAL (PRO)
# ================================

def _get_panel_notifications(request):
    qs = _user_qs(request)

    q = request.GET.get("q", "").strip()

    if q:
        qs = qs.filter(notification__message__icontains=q)

    return qs.order_by("-notification__created_at")


def _group_notifications_by_product(user_notifications):
    grouped = {}

    for un in user_notifications:
        n = un.notification
        key = n.product_id or "no-product"

        if key not in grouped:
            grouped[key] = {
                "product": n.product,
                "items": [],
                "count": 0,
                "has_unread": False,
                "icons": set(),
            }

        grouped[key]["items"].append(un)
        grouped[key]["count"] += 1

        if not un.seen:
            grouped[key]["has_unread"] = True

        icon = "🔔"
        if n.priority == "critical":
            icon = "🔴"
        elif n.priority == "warning":
            icon = "⚠️"

        grouped[key]["icons"].add(icon)

    grouped_list = list(grouped.values())

    grouped_list.sort(
        key=lambda g: max(un.notification.created_at for un in g["items"]),
        reverse=True
    )

    for g in grouped_list:
        g["items"].sort(key=lambda x: x.notification.created_at, reverse=True)
        g["icons"] = list(g["icons"])

    return grouped_list


def _panel_context(request, qs):
    return {
        "grouped_notifications": _group_notifications_by_product(qs),
        "has_unread": _has_unread(request),
    }


def notifications_panel(request):
    qs = _get_panel_notifications(request)
    context = _panel_context(request, qs)
    return render(request, "notifications/partials/panel.html", context)


def notifications_panel_mark_all(request):
    _user_qs(request).filter(seen=False).update(seen=True)

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


# ================================
# DASHBOARD
# ================================

def notifications_summary(request):
    qs = _user_qs(request)

    total = qs.count()
    unread = qs.filter(seen=False).count()

    by_type = (
        qs.values("notification__type")
        .annotate(c=Count("id"))
        .order_by()
    )

    return render(request, "dashboard/partials/notifications_summary.html", {
        "total_notifications": total,
        "unread_notifications": unread,
        "by_type": by_type,
    })


def notifications_chart(request):
    today = localdate()
    start = today - timedelta(days=29)

    qs = (
        _user_qs(request)
        .filter(notification__created_at__date__gte=start)
        .extra(select={"day": "date(notification.created_at)"})
        .values("day")
        .annotate(c=Count("id"))
        .order_by("day")
    )

    labels = [row["day"].strftime("%d/%m") for row in qs]
    values = [row["c"] for row in qs]

    return render(request, "dashboard/partials/notifications_chart.html", {
        "labels": labels,
        "values": values,
    })


def notifications_recent(request):
    recent = _user_qs(request).order_by("-notification__created_at")[:20]

    return render(
        request,
        "dashboard/partials/notifications_recent.html",
        {"notifications": [un.notification for un in recent]},
    )


# ================================
# TOGGLE GLOBAL
# ================================

def notifications_toggle_all(request):
    has_unread = _has_unread(request)

    if has_unread:
        _user_qs(request).filter(seen=False).update(seen=True)
        message = "Todas marcadas como leídas"
    else:
        _user_qs(request).update(seen=False)
        message = "Todas marcadas como no leídas"

    send_ui_event_to_all({
        "type": "notification",
        "message": message
    })

    if request.headers.get("HX-Request"):
        if "panel" in request.path:
            return notifications_panel(request)

        return notifications_list(request)

    return redirect("notifications_list")


# ================================
# BULK ACTIONS
# ================================

@require_POST
def notifications_bulk_action(request):
    action = request.POST.get("action")
    ids = request.POST.getlist("selected")

    if not ids:
        return notifications_list(request)

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
        return notifications_list(request)

    send_ui_event_to_all({
        "type": "notification",
        "message": message
    })

    if request.headers.get("HX-Request"):
        return notifications_list(request)

    return redirect("notifications_list")