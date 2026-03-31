from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔐 AUTH
    path('login/', LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # 👉 ROOT correcto → dashboard
    path('', lambda request: redirect('dashboard') if request.user.is_authenticated else redirect('login')),

    path('dashboard/', include('dashboard.urls')),

    path('inventory/', include('inventory.urls')),
    path('categorias/', include('categories.urls')),
    path('proveedores/', include('suppliers.urls')),
    path('productos/', include('products.urls')),

    path("movimientos/", lambda r: redirect("/stock-movements/")),
    path("stock-movements/", lambda r: redirect("/inventory/stock-movements/")),

    path('notificaciones/', include(('notifications.urls', 'notifications'), namespace='notifications')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)