from django.urls import path
from . import views

urlpatterns = [
    path("", views.observability_dashboard_view, name="observability_dashboard"),
    path("slow-requests/", views.slow_requests_view, name="observability_slow_requests"),
]