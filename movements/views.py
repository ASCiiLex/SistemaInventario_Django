from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.dateparse import parse_date
from .models import Movement
from products.models import Product
from .forms import MovementForm


def movement_list(request):
    search = request.GET.get("q", "")
    movement_type = request.GET.get("type", "")
    product_id = request.GET.get("product", "")
    date_from = request.GET.get("from", "")
    date_to = request.GET.get("to", "")

    movements = Movement.objects.select_related("product").all()

    if search:
        movements = movements.filter(product__name__icontains=search)

    if movement_type in ["IN", "OUT"]:
        movements = movements.filter(movement_type=movement_type)

    if product_id:
        movements = movements.filter(product_id=product_id)

    if date_from:
        df = parse_date(date_from)
        if df:
            movements = movements.filter(created_at__date__gte=df)

    if date_to:
        dt = parse_date(date_to)
        if dt:
            movements = movements.filter(created_at__date__lte=dt)

    products = Product.objects.all()

    context = {
        "movements": movements,
        "search": search,
        "movement_type": movement_type,
        "product_id": product_id,
        "date_from": date_from,
        "date_to": date_to,
        "products": products,
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