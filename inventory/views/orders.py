from django.shortcuts import render
from ..models import Order


def order_list(request):
    orders = Order.objects.select_related("supplier", "location").all()
    return render(request, "inventory/orders/list.html", {"orders": orders})