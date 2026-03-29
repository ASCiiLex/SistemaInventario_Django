import re
from ..models import Notification
from products.models import Product


def get_products():
    products_qs = Product.objects.all().values("id", "name")

    def natural_key(item):
        name = item["name"]
        return [
            int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', name)
        ]

    products_sorted = sorted(products_qs, key=natural_key)
    return [(p["id"], p["name"]) for p in products_sorted]


def get_filtered_notifications(request):
    status = request.GET.get("status", "")
    product_id = request.GET.get("product", "")
    type_filter = request.GET.get("type", "")
    priority = request.GET.get("priority", "")

    sort = request.GET.get("sort", "created_at")
    direction = request.GET.get("dir", "desc")

    order = f"-{sort}" if direction == "desc" else sort

    notifications = Notification.objects.select_related("product").order_by(order)

    if status == "new":
        notifications = notifications.filter(seen=False)
    elif status == "read":
        notifications = notifications.filter(seen=True)

    if product_id:
        notifications = notifications.filter(product_id=product_id)

    if type_filter:
        notifications = notifications.filter(type=type_filter)

    if priority:
        notifications = notifications.filter(priority=priority)

    return notifications, {
        "status": status,
        "product_id": product_id,
        "type": type_filter,
        "priority": priority,
        "current_sort": sort,
        "current_dir": direction,
    }


def group_notifications_by_product(notifications):
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

        if n.priority == "critical":
            grouped[key]["icons"].add("🔴")
        elif n.priority == "warning":
            grouped[key]["icons"].add("⚠️")
        else:
            grouped[key]["icons"].add("🔔")

    grouped_list = list(grouped.values())

    grouped_list.sort(
        key=lambda g: max(n.created_at for n in g["items"]),
        reverse=True
    )

    for g in grouped_list:
        g["items"].sort(key=lambda x: x.created_at, reverse=True)
        g["icons"] = list(g["icons"])

    return grouped_list
