from django.shortcuts import render
from .models import Location, Order


def location_list(request):
    locations = Location.objects.all()
    return render(request, "inventory/location_list.html", {"locations": locations})


def order_list(request):
    orders = Order.objects.select_related("supplier", "location").all()
    return render(request, "inventory/order_list.html", {"orders": orders})