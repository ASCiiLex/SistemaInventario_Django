from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Notification
from .utils import broadcast_notification


def _get_filtered_notifications(request):
    status = request.GET.get("status", "")
    product_id = request.GET.get("product", "")

    notifications = Notification.objects.select_related("product").order_by("-created_at")

    if status == "new":
        notifications = notifications.filter(seen=False)
    elif status == "read":
        notifications = notifications.filter(seen=True)

    if product_id:
        notifications = notifications.filter(product_id=product_id)

    return notifications, {
        "status": status,
        "product_id": product_id,
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

    # 🔥 Emitir WebSocket
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

    # 🔥 Emitir WebSocket
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


def notifications_counter(request):
    unread = Notification.objects.filter(seen=False).count()
    return render(request, "notifications/partials/bell.html", {"unread": unread})