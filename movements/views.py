from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Movement
from .forms import MovementForm


def movement_list(request):
    search = request.GET.get("q", "")
    movement_type = request.GET.get("type", "")

    movements = Movement.objects.select_related("product").all()

    if search:
        movements = movements.filter(product__name__icontains=search)

    if movement_type in ["IN", "OUT"]:
        movements = movements.filter(movement_type=movement_type)

    context = {
        "movements": movements,
        "search": search,
        "movement_type": movement_type,
    }
    return render(request, "movements/list.html", context)


def movement_create(request):
    if request.method == "POST":
        form = MovementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("movement_list"))
    else:
        form = MovementForm()

    return render(request, "movements/form.html", {
        "form": form,
        "title": "Nuevo Movimiento"
    })