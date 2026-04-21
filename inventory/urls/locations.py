from django.urls import path
from ..views.locations import (
    location_list,
    location_create,
    location_edit,
    location_delete,
    location_toggle_active,
    location_incidents,
    location_full_stock,
)

urlpatterns = [
    path("locations/", location_list, name="location_list"),
    path("locations/nuevo/", location_create, name="location_create"),
    path("locations/<int:pk>/editar/", location_edit, name="location_edit"),
    path("locations/<int:pk>/eliminar/", location_delete, name="location_delete"),
    path("locations/<int:pk>/activar/", location_toggle_active, name="location_toggle_active"),
    path("locations/<int:pk>/incidents/", location_incidents, name="location_incidents"),
    path("<int:pk>/stock/", location_full_stock, name="location_full_stock"),
]