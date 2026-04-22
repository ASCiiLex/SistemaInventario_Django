from django.shortcuts import render
from django.db.models import F, IntegerField, Sum, Value
from django.db.models.functions import Cast, Substr, Coalesce

from products.models import Product
from categories.models import Category
from suppliers.models import Supplier
from inventory.utils.listing import ListViewMixin


def product_list(request):
    view = ListViewMixin()
    view.allowed_sort_fields = [
        "name",
        "sku",
        "category__name",
        "supplier__name",
        "total_stock_db",
        "total_min_stock_db",
    ]
    view.default_ordering = "name"

    search = request.GET.get("q", "")
    category_id = request.GET.get("category", "")
    supplier_id = request.GET.get("supplier", "")
    stock_filter = request.GET.get("stock", "")

    products = (
        Product.objects
        .select_related("category", "supplier")
        .filter(organization=request.organization)
        .annotate(
            total_stock_db=Coalesce(Sum("stock_items__quantity"), Value(0)),
            total_min_stock_db=Coalesce(Sum("stock_items__min_stock"), Value(0)),
        )
    )

    if search:
        products = products.filter(name__icontains=search)

    if category_id:
        products = products.filter(category_id=category_id)

    if supplier_id:
        products = products.filter(supplier_id=supplier_id)

    if stock_filter == "low":
        products = products.filter(
            total_stock_db__lte=F("total_min_stock_db")
        )

    sort = request.GET.get("sort")
    direction = request.GET.get("dir", "asc")

    if sort == "sku":
        products = products.annotate(
            sku_number=Cast(Substr("sku", 4), IntegerField())
        )
        order_field = "sku_number"

    elif sort == "name":
        products = products.annotate(
            name_number=Cast(Substr("name", 9), IntegerField())
        )
        order_field = "name_number"

    elif sort in ["total_stock_db", "total_min_stock_db"]:
        order_field = sort

    else:
        products = view.apply_ordering(request, products)
        order_field = None

    if order_field:
        if direction == "desc":
            order_field = f"-{order_field}"
        products = products.order_by(order_field)

    page_obj = view.paginate_queryset(request, products)

    category_name = None
    supplier_name = None

    if category_id:
        category = Category.objects.filter(
            id=category_id,
            organization=request.organization
        ).first()
        if category:
            category_name = category.name

    if supplier_id:
        supplier = Supplier.objects.filter(
            id=supplier_id,
            organization=request.organization
        ).first()
        if supplier:
            supplier_name = supplier.name

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "search": search,
        "category_id": category_id,
        "supplier_id": supplier_id,
        "stock_filter": stock_filter,
        "category_name": category_name,
        "supplier_name": supplier_name,
        **view.get_ordering_context(request),
    }

    if view.is_htmx(request):
        return render(request, "products/partials/products_table.html", context)

    return render(request, "products/list.html", context)