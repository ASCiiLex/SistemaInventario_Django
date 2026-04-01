import re
from ..models import UserNotification
from products.models import Product


def user_qs(request):
    return UserNotification.objects.filter(user=request.user).select_related(
        "notification__product",
        "notification__location"
    )


def has_unread(request):
    return user_qs(request).filter(seen=False).exists()


def get_products():
    products_qs = Product.objects.all().values("id", "name")

    def natural_key(item):
        return [
            int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', item["name"])
        ]

    return [(p["id"], p["name"]) for p in sorted(products_qs, key=natural_key)]


def get_filtered_notifications(request):
    qs = user_qs(request)

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


def group_notifications_by_product(user_notifications):
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

        if n.type == "product_risk":
            icon = "⚠️"
        elif n.type == "stock_item_low":
            icon = "🔴"
        else:
            icon = "🔔"

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