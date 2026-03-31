from inventory.models import StockMovement


def get_recent_movements(limit=10):
    return (
        StockMovement.objects
        .select_related("product", "origin", "destination")
        .only(
            "id",
            "quantity",
            "movement_type",
            "created_at",
            "product__name",
            "origin__name",
            "destination__name",
        )
        .exclude(origin__isnull=True, destination__isnull=True)
        .order_by("-created_at")[:limit]
    )


def get_all_stock_movements():
    return (
        StockMovement.objects
        .select_related("product")
        .only(
            "id",
            "quantity",
            "movement_type",
            "created_at",
            "product__name",
        )
        .order_by("-created_at")
    )