from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Q

from products.models import Product
from inventory.models import StockItem, Order


def get_dashboard_metrics(org):
    # 🔹 Total unidades en stock
    total_units = (
        StockItem.objects.filter(organization=org)
        .aggregate(total=Sum("quantity"))["total"] or 0
    )

    # 🔹 Valor inventario
    inventory_value = (
        StockItem.objects.filter(organization=org)
        .annotate(
            item_value=ExpressionWrapper(
                F("quantity") * F("product__cost_price"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .aggregate(total=Sum("item_value"))["total"] or 0
    )

    # 🔹 Pedidos pendientes (incluye parcialmente recibidos)
    pending_orders = Order.objects.filter(
        organization=org
    ).filter(
        Q(status="pending") | Q(status="partially_received")
    ).count()

    # 🔹 Productos en riesgo
    product_risk_count = (
        StockItem.objects.filter(
            organization=org,
            quantity__lte=F("min_stock")
        )
        .values("product")
        .distinct()
        .count()
    )

    return {
        "total_units": total_units,
        "inventory_value": inventory_value,
        "pending_orders": pending_orders,
        "product_risk_count": product_risk_count,
    }


def get_low_stock(org):
    return StockItem.objects.filter(
        organization=org,
        quantity__lte=F("min_stock")
    ).select_related("product", "location")