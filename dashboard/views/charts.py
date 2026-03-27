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
    labels, values = get_chart_by_category()

    return render(
        request,
        "dashboard/partials/chart.html",
        {"chart_labels": labels, "chart_values": values},
    )


def dashboard_chart_data(request, tipo):
    if tipo == "categorias":
        labels, values = get_chart_by_category()
    elif tipo == "proveedores":
        labels, values = get_chart_by_supplier()
    elif tipo == "almacenes":
        labels, values = get_chart_by_location()
    elif tipo == "rotacion":
        labels, values = get_chart_rotation_by_product()
    elif tipo == "movimientos":
        labels, values = get_chart_movements_by_type()
    else:
        labels, values = [], []

    return JsonResponse({"labels": labels, "values": values})