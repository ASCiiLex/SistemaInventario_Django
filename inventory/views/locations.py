from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q, F, OuterRef, Subquery

from ..models import Location, StockItem
from ..forms import LocationForm
from ..utils.listing import ListViewMixin

from notifications.models import Notification
from notifications.constants import Events

import re


# ==========================================
# LIST
# ==========================================

def location_list(request):
    view = ListViewMixin()
    view.allowed_sort_fields = ["name", "address", "is_active"]
    view.default_ordering = "name"

    qs = (
        Location.objects
        .filter(organization=request.organization)
        .annotate(
            low_stock_count=Count(
                "stock_items",
                filter=Q(stock_items__quantity__lte=F("stock_items__min_stock"))
            ),
            total_products=Count("stock_items")
        )
    )

    search = request.GET.get("q")
    if search:
        qs = qs.filter(name__icontains=search)

    qs = view.apply_ordering(request, qs)
    page_obj = view.paginate_queryset(request, qs)

    context = {
        "locations": page_obj,
        "page_obj": page_obj,
        "search": search or "",
        "current_sort": request.GET.get("sort", ""),
        "current_dir": request.GET.get("dir", "asc"),
    }

    if view.is_htmx(request):
        return render(request, "inventory/locations/partials/table.html", context)

    return render(request, "inventory/locations/list.html", context)


# ==========================================
# INCIDENTS
# ==========================================

def location_incidents(request, pk):
    location = get_object_or_404(
        Location,
        pk=pk,
        organization=request.organization
    )

    view = ListViewMixin()
    view.allowed_sort_fields = [
        "product__name",
        "quantity",
        "min_stock",
        "last_alert",
    ]
    view.default_ordering = "product__name"

    latest_notification = Notification.objects.filter(
        organization=request.organization,
        product=OuterRef("product"),
        location=location,
        type=Events.STOCK_LOW,
    ).order_by("-created_at")

    qs = (
        StockItem.objects
        .select_related("product")
        .filter(
            organization=request.organization,
            location=location,
            quantity__lte=F("min_stock")
        )
        .annotate(
            last_alert=Subquery(latest_notification.values("created_at")[:1])
        )
    )

    sort = request.GET.get("sort")
    direction = request.GET.get("dir", "asc")

    if sort == "product__name":
        qs = sorted(
            qs,
            key=lambda x: [
                int(t) if t.isdigit() else t.lower()
                for t in re.split(r'(\d+)', x.product.name)
            ],
            reverse=(direction == "desc")
        )
    else:
        qs = view.apply_ordering(request, qs)

    context = {
        "items": qs,
        "target_id": f"#expand-{pk}",
        "base_url": request.path,
        **view.get_ordering_context(request),
    }

    return render(request, "inventory/locations/partials/incidents.html", context)


# ==========================================
# CREATE
# ==========================================

def location_create(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.organization = request.organization
            location.save()

            messages.success(request, "Almacén creado correctamente.")
            return redirect("location_list")
    else:
        form = LocationForm()

    return render(
        request,
        "inventory/locations/form.html",
        {"form": form, "title": "Nuevo almacén"},
    )


# ==========================================
# EDIT
# ==========================================

def location_edit(request, pk):
    location = get_object_or_404(
        Location,
        pk=pk,
        organization=request.organization
    )

    if request.method == "POST":
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, "Almacén actualizado correctamente.")
            return redirect("location_list")
    else:
        form = LocationForm(instance=location)

    return render(
        request,
        "inventory/locations/form.html",
        {"form": form, "title": f"Editar almacén: {location.name}"},
    )


# ==========================================
# DELETE
# ==========================================

def location_delete(request, pk):
    location = get_object_or_404(
        Location,
        pk=pk,
        organization=request.organization
    )

    if request.method == "POST":
        location.delete()
        messages.success(request, "Almacén eliminado correctamente.")
        return redirect("location_list")

    return render(
        request,
        "inventory/locations/delete.html",
        {"location": location},
    )


# ==========================================
# TOGGLE
# ==========================================

def location_toggle_active(request, pk):
    location = get_object_or_404(
        Location,
        pk=pk,
        organization=request.organization
    )

    location.is_active = not location.is_active
    location.save()

    messages.success(request, "Estado de almacén actualizado.")
    return redirect("location_list")


# ==========================================
# FULL STOCK (FIX CLAVE)
# ==========================================

def location_full_stock(request, pk):
    location = get_object_or_404(
        Location,
        pk=pk,
        organization=request.organization
    )

    mode = request.GET.get("mode", "all")

    latest_notification = Notification.objects.filter(
        organization=request.organization,
        product=OuterRef("product"),
        location=location,
        type=Events.STOCK_LOW,
    ).order_by("-created_at")

    qs = (
        StockItem.objects
        .select_related("product")
        .filter(
            organization=request.organization,
            location=location
        )
        .annotate(
            last_alert=Subquery(latest_notification.values("created_at")[:1])
        )
    )

    # 🔥 IMPORTANTE: forzamos evaluación para evitar problemas con HTMX + lazy queryset
    qs = list(qs)

    if mode == "incidents":
        qs = [item for item in qs if item.quantity <= item.min_stock]

    return render(request, "inventory/locations/partials/full_stock.html", {
        "items": qs,
        "mode": mode,
        "location_id": location.id
    })