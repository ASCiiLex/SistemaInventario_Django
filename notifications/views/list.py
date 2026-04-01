from django.shortcuts import render
from .utils import get_filtered_notifications, get_products, has_unread


def notifications_list(request):
    qs, filters_ctx = get_filtered_notifications(request)

    context = {
        "user_notifications": qs,
        "notifications": [un.notification for un in qs],
        "products": get_products(request),
        "has_unread": has_unread(request),
        **filters_ctx,
    }

    if request.headers.get("HX-Request"):
        return render(request, "notifications/partials/notifications_table.html", context)

    return render(request, "notifications/list.html", context)