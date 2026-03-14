from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import localdate
from django.core.paginator import Paginator
from django.db.models import Count
from datetime import timedelta

from .models import Notification
from .utils import broadcast_notification


# LISTA PRINCIPAL (tabla)

def _get_filtered_notifications(request):
    status = request.GET.get("status", "")
    product_id = request.GET.get("product", "")
    type_filter = request.GET.get("type", "")

    notifications = Notification.objects.select_related("product").order_by("-created_at")

    if status == "new":
        notifications = notifications.filter(seen=False)
    elif status == "read":
        notifications = notifications.filter(seen=True)

    if product_id:
        notifications = notifications.filter(product_id=product_id)

    if type_filter:
        notifications = notifications.filter(type=type_filter)

    return notifications, {
        "status": status,
        "product_id": product_id,
        "type": type_filter,
    }


def notifications_list(request):
    notifications, filters_ctx = _get_filtered_notifications(request)

    products = (
        Notification.objects.exclude(product__isnull=True)
        .values_list("product_id", "product__name")
        .distinct()
    )

    context = {
        "notifications": notifications,
        "products": products,
        **filters_ctx,
    }

    if request.headers.get("HX-Request"):
        return render(request, "notifications/partials/notifications_table.html", context)

    return render(request, "notifications/list.html", context)


def notifications_mark_all_read(request):
    Notification.objects.filter(seen=False).update(seen=True)

    broadcast_notification({
        "type": "notification",
        "message": "Todas las notificaciones marcadas como leídas"
    })

    if request.headers.get("HX-Request"):
        notifications, filters_ctx = _get_filtered_notifications(request)
        products = (
            Notification.objects.exclude(product__isnull=True)
            .values_list("product_id", "product__name")
            .distinct()
        )
        context = {
            "notifications": notifications,
            "products": products,
            **filters_ctx,
        }
        response = render(request, "notifications/partials/notifications_table.html", context)
        response["HX-Trigger"] = '{"notifications-updated": {"message": "Notificaciones actualizadas"}}'
        return response

    return redirect("notifications_list")


def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.seen = True
    notification.save()

    broadcast_notification({
        "type": "notification",
        "message": "Notificación marcada como leída"
    })

    if request.headers.get("HX-Request"):
        notifications, filters_ctx = _get_filtered_notifications(request)
        products = (
            Notification.objects.exclude(product__isnull=True)
            .values_list("product_id", "product__name")
            .distinct()
        )
        context = {
            "notifications": notifications,
            "products": products,
            **filters_ctx,
        }
        response = render(request, "notifications/partials/notifications_table.html", context)
        response["HX-Trigger"] = '{"notifications-updated": {"message": "Notificación marcada como leída"}}'
        return response

    return redirect("notifications_list")


def notification_mark_unread(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.seen = False
    notification.save()

    broadcast_notification({
        "type": "notification",
        "message": "Notificación marcada como no leída"
    })

    notifications, filters_ctx = _get_filtered_notifications(request)
    products = (
        Notification.objects.exclude(product__isnull=True)
        .values_list("product_id", "product__name")
        .distinct()
    )
    context = {
        "notifications": notifications,
        "products": products,
        **filters_ctx,
    }
    response = render(request, "notifications/partials/notifications_table.html", context)
    response["HX-Trigger"] = '{"notifications-updated": {"message": "Notificación marcada como no leída"}}'
    return response


# CAMPANA

def notifications_counter(request):
    unread = Notification.objects.filter(seen=False).count()
    return render(request, "notifications/partials/bell.html", {"unread": unread})


# PANEL LATERAL

def _get_panel_notifications(request):
    q = request.GET.get("q", "").strip().lower()
    page = request.GET.get("page", 1)

    notifications = Notification.objects.select_related("product").order_by("-created_at")

    if q:
        notifications = notifications.filter(message__icontains=q)

    paginator = Paginator(notifications, 10)
    page_obj = paginator.get_page(page)

    return page_obj


def _panel_context(page_obj):
    today = localdate()
    yesterday = today - timedelta(days=1)
    week_start = today - timedelta(days=today.weekday())

    return {
        "page_obj": page_obj,
        "notifications": page_obj.object_list,
        "today": today,
        "yesterday": yesterday,
        "week_start": week_start,
    }


def notifications_panel(request):
    page_obj = _get_panel_notifications(request)
    context = _panel_context(page_obj)
    return render(request, "notifications/partials/panel.html", context)


def notifications_panel_mark_all(request):
    Notification.objects.filter(seen=False).update(seen=True)

    broadcast_notification({
        "type": "notification",
        "message": "Todas las notificaciones marcadas como leídas"
    })

    page_obj = _get_panel_notifications(request)
    context = _panel_context(page_obj)

    response = render(request, "notifications/partials/panel.html", context)
    response["HX-Trigger"] = '{"notifications-updated": {"message": "Notificaciones actualizadas"}}'
    return response


def notifications_panel_mark_one(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.seen = True
    notification.save()

    broadcast_notification({
        "type": "notification",
        "message": "Notificación marcada como leída"
    })

    page_obj = _get_panel_notifications(request)
    context = _panel_context(page_obj)

    response = render(request, "notifications/partials/panel.html", context)
    response["HX-Trigger"] = '{"notifications-updated": {"message": "Notificación marcada como leída"}}'
    return response


def notifications_panel_mark_unread(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.seen = False
    notification.save()

    broadcast_notification({
        "type": "notification",
        "message": "Notificación marcada como no leída"
    })

    page_obj = _get_panel_notifications(request)
    context = _panel_context(page_obj)

    response = render(request, "notifications/partials/panel.html", context)
    response["HX-Trigger"] = '{"notifications-updated": {"message": "Notificación marcada como no leída"}}'
    return response


# ENDPOINTS PARA DASHBOARD DE ACTIVIDAD

def notifications_summary(request):
    total = Notification.objects.count()
    unread = Notification.objects.filter(seen=False).count()
    by_type = (
        Notification.objects
        .values("type")
        .annotate(c=Count("id"))
        .order_by()
    )
    context = {
        "total_notifications": total,
        "unread_notifications": unread,
        "by_type": by_type,
    }
    return render(request, "dashboard/partials/notifications_summary.html", context)


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

    by_type = (
        Notification.objects
        .values("type")
        .annotate(c=Count("id"))
        .order_by()
    )
    type_labels = [row["type"] or "info" for row in by_type]
    type_values = [row["c"] for row in by_type]

    read_count = Notification.objects.filter(seen=True).count()
    unread_count = Notification.objects.filter(seen=False).count()

    context = {
        "labels": labels,
        "values": values,
        "type_labels": type_labels,
        "type_values": type_values,
        "read_count": read_count,
        "unread_count": unread_count,
    }
    return render(request, "dashboard/partials/notifications_chart.html", context)


def notifications_recent(request):
    recent = Notification.objects.select_related("product").order_by("-created_at")[:20]
    return render(
        request,
        "dashboard/partials/notifications_recent.html",
        {"notifications": recent},
    )