from django.shortcuts import render, redirect
from .models import Notification


def notifications_list(request):
    notifications = Notification.objects.order_by("-created_at")
    return render(request, "notifications/list.html", {"notifications": notifications})


def notifications_mark_all_read(request):
    Notification.objects.filter(seen=False).update(seen=True)
    return redirect("notifications_list")


def notifications_counter(request):
    unread = Notification.objects.filter(seen=False).count()
    return render(request, "notifications/partials/bell.html", {"unread": unread})