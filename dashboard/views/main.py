from django.shortcuts import render

from dashboard.services.metrics import get_dashboard_metrics
from dashboard.services.charts import get_chart_by_category
from dashboard.services.notifications import get_notifications_summary

# 🔥 IMPORTANTE → SERVICE CENTRAL
from inventory.services.stock_alerts import sync_all_notifications


def dashboard_view(request):
    # 🔥 SINGLE SOURCE OF TRUTH
    sync_all_notifications()

    metrics = get_dashboard_metrics()
    chart_labels, chart_values = get_chart_by_category()
    notifications = get_notifications_summary()

    context = {
        **metrics,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
        **notifications,
    }

    return render(request, "dashboard/dashboard.html", context)