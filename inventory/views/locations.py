from django.shortcuts import render
from ..models import Location


def location_list(request):
    locations = Location.objects.all()
    return render(request, "inventory/locations/list.html", {"locations": locations})