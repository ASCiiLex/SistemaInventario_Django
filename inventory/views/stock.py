from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from ..models import StockMovement
from ..forms import StockMovementForm


def stockmovement_list(request):
    movements = StockMovement.objects.select_related("product", "origin", "destination").all()
    return render(request, "inventory/stock/list.html", {"movements": movements})


def stockmovement_create(request):
    if request.method == "POST":
        form = StockMovementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("stockmovement_list"))
    else:
        form = StockMovementForm()

    return render(
        request,
        "inventory/stock/form.html",
        {"form": form, "title": "Nuevo movimiento de stock"},
    )