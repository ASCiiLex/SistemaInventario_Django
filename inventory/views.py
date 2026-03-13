from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Location, Order, StockMovement
from .forms import StockMovementForm, StockTransferForm


def location_list(request):
    locations = Location.objects.all()
    return render(request, "inventory/location_list.html", {"locations": locations})


def order_list(request):
    orders = Order.objects.select_related("supplier", "location").all()
    return render(request, "inventory/order_list.html", {"orders": orders})


def stockmovement_list(request):
    movements = StockMovement.objects.select_related("product", "origin", "destination").all()
    return render(request, "inventory/stockmovement_list.html", {"movements": movements})


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
        "inventory/stockmovement_form.html",
        {
            "form": form,
            "title": "Nuevo movimiento de stock",
        },
    )


def stock_transfer_create(request):
    if request.method == "POST":
        form = StockTransferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("stockmovement_list"))
    else:
        form = StockTransferForm()

    return render(
        request,
        "inventory/stock_transfer_form.html",
        {
            "form": form,
            "title": "Transferencia entre almacenes",
        },
    )