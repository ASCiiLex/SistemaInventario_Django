from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from django.contrib.auth.views import LoginView, LogoutView

# 🔥 PROMETHEUS
from django.http import HttpResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from core.views.dev import create_admin


def metrics_view(request):
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("create-admin/", create_admin),

    # 🔐 AUTH
    path('login/', LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # ROOT
    path('', lambda request: redirect('dashboard') if request.user.is_authenticated else redirect('login')),

    path('dashboard/', include('dashboard.urls')),

    path("accounts/", include("accounts.urls")),

    path('inventory/', include('inventory.urls')),
    path('categorias/', include('categories.urls')),
    path('proveedores/', include('suppliers.urls')),
    path('productos/', include('products.urls')),

    path('organization/', include('organizations.urls')),

    path("movimientos/", lambda r: redirect("/stock-movements/")),
    path("stock-movements/", lambda r: redirect("/inventory/stock-movements/")),

    path('notificaciones/', include(('notifications.urls', 'notifications'), namespace='notifications')),

    # 🔥 METRICS ENDPOINT
    path('metrics/', metrics_view, name='metrics'),
    path("observability/", include("observability.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)