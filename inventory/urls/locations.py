from django.urls import path
from ..views import location_list

urlpatterns = [
    path("locations/", location_list, name="location_list"),
]