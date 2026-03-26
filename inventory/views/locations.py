from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from ..models import Location
from ..forms import LocationForm
from ..utils.listing import ListViewMixin


def location_list(request):
    view = ListViewMixin()

    qs = Location.objects.all()

    search = request.GET.get("q")
    if search:
        qs = qs.filter(name__icontains=search)

    page_obj = view.paginate_queryset(request, qs)

    context = {
        "locations": page_obj,
        "page_obj": page_obj,
        "search": search or "",
    }

    if view.is_htmx(request):
        return render(request, "inventory/locations/partials/table.html", context)

    return render(request, "inventory/locations/list.html", context)


def location_create(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Almacén creado correctamente.")
            return redirect("location_list")
    else:
        form = LocationForm()

    return render(
        request,
        "inventory/locations/form.html",
        {"form": form, "title": "Nuevo almacén"},
    )


def location_edit(request, pk):
    location = get_object_or_404(Location, pk=pk)

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


def location_delete(request, pk):
    location = get_object_or_404(Location, pk=pk)

    if request.method == "POST":
        location.delete()
        messages.success(request, "Almacén eliminado correctamente.")
        return redirect("location_list")

    return render(
        request,
        "inventory/locations/delete.html",
        {"location": location},
    )


def location_toggle_active(request, pk):
    location = get_object_or_404(Location, pk=pk)
    location.is_active = not location.is_active
    location.save()
    messages.success(request, "Estado de almacén actualizado.")
    return redirect("location_list")