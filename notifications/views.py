from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Notification


def notifications_list(request):
    notifications = Notification.objects.order_by("-created_at")
    context = {"notifications": notifications}

    if request.headers.get("HX-Request"):
        return render(request, "notifications/partials/notifications_table.html", context)

    return render(request, "notifications/list.html", context)


def notifications_mark_all_read(request):
    Notification.objects.filter(seen=False).update(seen=True)

    if request.headers.get("HX-Request"):
        notifications = Notification.objects.order_by("-created_at")
        context = {"notifications": notifications}
        response = render(request, "notifications/partials/notifications_table.html", context)
        response["HX-Trigger"] = "notifications-updated"
        return response

    return redirect("notifications_list")


def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.seen = True
    notification.save()

    if request.headers.get("HX-Request"):
        notifications = Notification.objects.order_by("-created_at")
        context = {"notifications": notifications}
        response = render(request, "notifications/partials/notifications_table.html", context)
        response["HX-Trigger"] = "notifications-updated"
        return response

    return redirect("notifications_list")


def notifications_counter(request):
    unread = Notification.objects.filter(seen=False).count()
    return render(request, "notifications/partials/bell.html", {"unread": unread})