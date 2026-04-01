from django.shortcuts import render
from dashboard.services.activity import (
    get_recent_movements,
    get_all_stock_movements,
)


def dashboard_recent_movements(request):
    movements = get_recent_movements(request.organization)
    return render(
        request,
        "dashboard/partials/recent_movements.html",
        {"movements": movements},
    )


def dashboard_recent_stock_movements(request):
    stock_movements = get_all_stock_movements(request.organization)
    return render(
        request,
        "dashboard/partials/recent_stock_movements.html",
        {"stock_movements": stock_movements},
    )