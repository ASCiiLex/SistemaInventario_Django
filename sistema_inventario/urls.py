from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


urlpatterns = [
    path('admin/', admin.site.urls),

    # Página principal → Dashboard
    path('', include('dashboard.urls')),

    # Inventario
    path('inventory/', include('inventory.urls')),
    path('categorias/', include('categories.urls')),
    path('proveedores/', include('suppliers.urls')),
    path('productos/', include('products.urls')),
    path("movimientos/", lambda r: redirect("/stock-movements/")),
    path("stock-movements/", lambda r: redirect("/inventory/stock-movements/")),

    

    # Notificaciones
    path('notificaciones/', include('notifications.urls')),
]

# Archivos multimedia (imágenes de productos)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)