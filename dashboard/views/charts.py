from django.shortcuts import render
from django.http import JsonResponse

from dashboard.services.charts import (
    get_chart_by_category,
    get_chart_by_supplier,
    get_chart_by_location,
    get_chart_rotation_by_product,
    get_chart_movements_by_type,
)


def dashboard_chart(request):
    if not request.organization:
        return render(
            request,
            "dashboard/partials/chart.html",
            {"chart_labels": [], "chart_values": []},
        )

    labels, values = get_chart_by_category(request.organization)

    return render(
        request,
        "dashboard/partials/chart.html",
        {"chart_labels": labels, "chart_values": values},
    )


def dashboard_chart_data(request, tipo):
    if not request.organization:
        return JsonResponse({"labels": [], "values": []})

    org = request.organization

    if tipo == "categorias":
        labels, values = get_chart_by_category(org)
    elif tipo == "proveedores":
        labels, values = get_chart_by_supplier(org)
    elif tipo == "almacenes":
        labels, values = get_chart_by_location(org)
    elif tipo == "rotacion":
        labels, values = get_chart_rotation_by_product(org)
    elif tipo == "movimientos":
        labels, values = get_chart_movements_by_type(org)
    else:
        labels, values = [], []

    return JsonResponse({"labels": labels, "values": values})