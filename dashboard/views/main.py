from django.shortcuts import render


def dashboard_view(request):
    if not hasattr(request, "organization") or not request.organization:
        return render(request, "dashboard/dashboard.html", {})

    return render(request, "dashboard/dashboard.html", {})