import re
from datetime import timedelta
from django.utils import timezone

from ..models import UserNotification
from products.models import Product


ICON_MAP = {
    "inventory:product_risk": "⚠️",
    "inventory:stock_low": "🔴",
    "inventory:movement_created": "🔔",
    "orders:updated": "📦",
}


def _get_icon(type_):
    return ICON_MAP.get(type_, "🔔")


def user_qs(request):
    return (
        UserNotification.objects
        .filter(
            user=request.user,
            notification__organization=request.organization
        )
        .select_related(
            "notification__product",
            "notification__location"
        )
    )


def has_unread(request):
    return user_qs(request).filter(seen=False).exists()


def get_products(request):
    products_qs = Product.objects.filter(
        organization=request.organization
    ).values("id", "name")

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
    now = timezone.now()
    cutoff = now - timedelta(days=7)
    MAX_RECENT = 3

    for un in user_notifications:
        n = un.notification
        key = n.product_id or "no-product"

        if key not in grouped:
            grouped[key] = {
                "product": n.product,
                "all_items": [],
                "items": [],
                "count": 0,
                "has_unread": False,
                "icons": set(),
                "hidden_count": 0,
            }

        grouped[key]["all_items"].append(un)

        if not un.seen:
            grouped[key]["has_unread"] = True

        grouped[key]["icons"].add(_get_icon(n.type))

    grouped_list = []

    for g in grouped.values():
        # ordenar todo
        items = sorted(
            g["all_items"],
            key=lambda x: x.notification.created_at,
            reverse=True
        )

        g["count"] = len(items)

        # 🔥 lógica: última + recientes
        latest = items[0]
        recent = [
            i for i in items[1:]
            if i.notification.created_at >= cutoff
        ][:MAX_RECENT]

        final_items = [latest] + recent

        g["items"] = final_items
        g["hidden_count"] = max(0, len(items) - len(final_items))

        grouped_list.append(g)

    grouped_list.sort(
        key=lambda g: g["items"][0].notification.created_at,
        reverse=True
    )

    for g in grouped_list:
        g["icons"] = list(g["icons"])

    return grouped_list