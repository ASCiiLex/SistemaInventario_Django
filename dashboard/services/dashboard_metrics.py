from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Q, IntegerField
from django.db.models.functions import Cast, Substr
from django.db.models.expressions import Func

from products.models import Product
from inventory.models import StockItem, Order


class RegexpReplace(Func):
    function = "REGEXP_REPLACE"
    arity = 3


# ==========================================
# 🔥 HELPERS DE DOMINIO (ALINEADOS CON NOTIFICATIONS)
# ==========================================

def _get_products_in_risk(org):
    products = Product.objects.filter(organization=org)

    risk_count = 0

    for p in products:
        agg = (
            StockItem.objects
            .filter(organization=org, product=p)
            .aggregate(
                total_qty=Sum("quantity"),
                total_min=Sum("min_stock"),
            )
        )

        total_qty = agg["total_qty"] or 0
        total_min = agg["total_min"] or 0

        has_local_issue = StockItem.objects.filter(
            organization=org,
            product=p,
            quantity__lte=F("min_stock")
        ).exists()

        if has_local_issue and total_qty <= total_min:
            risk_count += 1

    return risk_count


# ==========================================
# METRICS
# ==========================================

def get_dashboard_metrics(org):
    total_units = (
        StockItem.objects.filter(organization=org)
        .aggregate(total=Sum("quantity"))["total"] or 0
    )

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

    pending_orders = Order.objects.filter(
        organization=org
    ).filter(
        Q(status="pending") | Q(status="partially_received")
    ).count()

    product_risk_count = _get_products_in_risk(org)

    return {
        "total_units": total_units,
        "inventory_value": inventory_value,
        "pending_orders": pending_orders,
        "product_risk_count": product_risk_count,
    }


# ==========================================
# LOW STOCK (NIVEL UBICACIÓN)
# ==========================================

def get_low_stock(org):
    qs = (
        StockItem.objects.filter(
            organization=org,
            quantity__lte=F("min_stock")
        )
        .select_related("product", "location")
    )

    # 🔥 Natural sorting para product__name
    qs = qs.annotate(
        product_name_num=Cast(
            RegexpReplace(F("product__name"), r"\D", ""),
            IntegerField()
        )
    )

    return qs