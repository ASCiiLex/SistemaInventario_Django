from django.shortcuts import render
from .utils import get_filtered_notifications, get_products
from ..models import Notification


def notifications_list(request):
    notifications, filters_ctx = get_filtered_notifications(request)

    context = {
        "notifications": notifications,
        "products": get_products(),
        "has_unread": Notification.objects.filter(seen=False).exists(),
        **filters_ctx,
    }

    if request.headers.get("HX-Request"):
        return render(request, "notifications/partials/notifications_table.html", context)

    return render(request, "notifications/list.html", context)
