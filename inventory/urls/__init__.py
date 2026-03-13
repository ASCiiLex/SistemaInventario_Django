from .stock import urlpatterns as stock_urls
from .transfers import urlpatterns as transfer_urls
from .imports import urlpatterns as import_urls
from .locations import urlpatterns as location_urls
from .orders import urlpatterns as order_urls

urlpatterns = (
    stock_urls +
    transfer_urls +
    import_urls +
    location_urls +
    order_urls
)