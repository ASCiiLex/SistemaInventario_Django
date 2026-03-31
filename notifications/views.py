from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import localdate
from django.views.decorators.http import require_POST
from django.db.models import Count
from datetime import timedelta

from .models import Notification
from .utils import send_ui_event_to_all

from products.models import Product


# ================================
# HELPERS
# ================================

def _has_unread():
    return Notification.objects.filter(seen=False).exists()


def _base_context(notifications, extra=None):
    context = {
        "notifications": notifications,
        "products": _get_products(),
        "has_unread": _has_unread(),
    }
    if extra:
        context.update(extra)
    return context


# ================================
# LISTA PRINCIPAL (TABLA)
# ================================

def _get_filtered_notifications(request):
    status = request.GET.get("status", "")
    product_id = request.GET.get("product", "")
    type_filter = request.GET.get("type", "")
    priority = request.GET.get("priority", "")

    sort = request.GET.get("sort", "created_at")
    direction = request.GET.get("dir", "desc")

    order = f"-{sort}" if direction == "desc" else sort

    qs = Notification.objects.select_related("product").order_by(order)

    if status == "new":
        qs = qs.filter(seen=False)
    elif status == "read":
        qs = qs.filter(seen=True)

    if product_id:
        qs = qs.filter(product_id=product_id)

    if type_filter:
        qs = qs.filter(type=type_filter)

    if priority:
        qs = qs.filter(priority=priority)

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

    products_sorted = sorted(products_qs, key=natural_key)
    return [(p["id"], p["name"]) for p in products_sorted]


def notifications_list(request):
    notifications, filters_ctx = _get_filtered_notifications(request)

    context = _base_context(notifications, filters_ctx)

    if request.headers.get("HX-Request"):
        return render(request, "notifications/partials/notifications_table.html", context)

    return render(request, "notifications/list.html", context)


# ================================
# ACCIONES TABLA
# ================================

def notifications_mark_all_read(request):
    Notification.objects.filter(seen=False).update(seen=True)

    send_ui_event_to_all({
        "type": "notification",
        "message": "Todas las notificaciones marcadas como leídas"
    })

    notifications, filters_ctx = _get_filtered_notifications(request)
    context = _base_context(notifications, filters_ctx)

    response = render(request, "notifications/partials/notifications_table.html", context)
    response["HX-Trigger"] = '{"inventory:notifications_updated": true}'
    return response


def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.seen = True
    notification.save(update_fields=["seen"])

    send_ui_event_to_all({
        "type": "notification",
        "message": "Notificación marcada como leída"
    })

    return notifications_mark_all_read(request)


def notification_mark_unread(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.seen = False
    notification.save(update_fields=["seen"])

    send_ui_event_to_all({
        "type": "notification",
        "message": "Notificación marcada como no leída"
    })

    return notifications_mark_all_read(request)


# ================================
# CONTADOR NAVBAR
# ================================

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
# PANEL LATERAL (PRO)
# ================================

def _get_panel_notifications(request):
    q = request.GET.get("q", "").strip()

    qs = Notification.objects.select_related("product").order_by("-created_at")

    if q:
        qs = qs.filter(message__icontains=q)

    return qs


def _group_notifications_by_product(notifications):
    grouped = {}

    for n in notifications:
        key = n.product_id or "no-product"

        if key not in grouped:
            grouped[key] = {
                "product": n.product,
                "items": [],
                "count": 0,
                "has_unread": False,
                "icons": set(),
            }

        grouped[key]["items"].append(n)
        grouped[key]["count"] += 1

        if not n.seen:
            grouped[key]["has_unread"] = True

        icon = "🔔"
        if n.priority == "critical":
            icon = "🔴"
        elif n.priority == "warning":
            icon = "⚠️"

        grouped[key]["icons"].add(icon)

    grouped_list = list(grouped.values())

    grouped_list.sort(
        key=lambda g: max(n.created_at for n in g["items"]),
        reverse=True
    )

    for g in grouped_list:
        g["items"].sort(key=lambda x: x.created_at, reverse=True)
        g["icons"] = list(g["icons"])

    return grouped_list


def _panel_context(notifications):
    return {
        "grouped_notifications": _group_notifications_by_product(notifications),
        "has_unread": _has_unread(),
    }


def notifications_panel(request):
    notifications = _get_panel_notifications(request)
    context = _panel_context(notifications)
    return render(request, "notifications/partials/panel.html", context)


def notifications_panel_mark_all(request):
    Notification.objects.filter(seen=False).update(seen=True)

    send_ui_event_to_all({
        "type": "notification",
        "message": "Todas las notificaciones marcadas como leídas"
    })

    return notifications_panel(request)


def notifications_panel_mark_one(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.seen = True
    notification.save(update_fields=["seen"])

    send_ui_event_to_all({
        "type": "notification",
        "message": "Notificación marcada como leída"
    })

    return notifications_panel(request)


def notifications_panel_mark_unread(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.seen = False
    notification.save(update_fields=["seen"])

    send_ui_event_to_all({
        "type": "notification",
        "message": "Notificación marcada como no leída"
    })

    return notifications_panel(request)


# ================================
# DASHBOARD
# ================================

def notifications_summary(request):
    total = Notification.objects.count()
    unread = Notification.objects.filter(seen=False).count()

    by_type = (
        Notification.objects
        .values("type")
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
        Notification.objects.filter(created_at__date__gte=start)
        .extra(select={"day": "date(created_at)"})
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
    recent = Notification.objects.select_related("product").order_by("-created_at")[:20]

    return render(
        request,
        "dashboard/partials/notifications_recent.html",
        {"notifications": recent},
    )


# ================================
# TOGGLE GLOBAL
# ================================

def notifications_toggle_all(request):
    has_unread = _has_unread()

    if has_unread:
        Notification.objects.filter(seen=False).update(seen=True)
        message = "Todas marcadas como leídas"
    else:
        Notification.objects.update(seen=False)
        message = "Todas marcadas como no leídas"

    send_ui_event_to_all({
        "type": "notification",
        "message": message
    })

    if request.headers.get("HX-Request"):
        if "panel" in request.path:
            return notifications_panel(request)

        notifications, filters_ctx = _get_filtered_notifications(request)
        context = _base_context(notifications, filters_ctx)

        response = render(request, "notifications/partials/notifications_table.html", context)
        response["HX-Trigger"] = '{"inventory:notifications_updated": true}'
        return response

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

    qs = Notification.objects.filter(id__in=ids)

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
        notifications, filters_ctx = _get_filtered_notifications(request)
        context = _base_context(notifications, filters_ctx)

        response = render(request, "notifications/partials/notifications_table.html", context)
        response["HX-Trigger"] = '{"inventory:notifications_updated": true}'
        return response

    return redirect("notifications_list")