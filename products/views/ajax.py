from django.http import JsonResponse
from django.shortcuts import render

from categories.models import Category
from suppliers.models import Supplier
from inventory.models import StockItem


def ajax_categories(request):
    q = request.GET.get("q", "")

    qs = Category.objects.filter(
        organization=request.organization
    )

    if q:
        qs = qs.filter(name__icontains=q)

    data = [
        {"id": c.id, "text": c.name}
        for c in qs.order_by("name")[:20]
    ]

    return JsonResponse({"results": data})


def ajax_suppliers(request):
    q = request.GET.get("q", "")

    qs = Supplier.objects.filter(
        organization=request.organization
    )

    if q:
        qs = qs.filter(name__icontains=q)

    data = [
        {"id": s.id, "text": s.name}
        for s in qs.order_by("name")[:20]
    ]

    return JsonResponse({"results": data})


def product_locations(request, pk):
    items = (
        StockItem.objects
        .select_related("location")
        .filter(
            organization=request.organization,
            product_id=pk
        )
    )

    return render(request, "products/partials/locations.html", {
        "items": items
    })