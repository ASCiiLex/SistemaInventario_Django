from organizations.models import Organization
from products.models import Product
from categories.models import Category
from suppliers.models import Supplier
from inventory.models import Location, StockItem, Order, OrderItem, StockMovement, StockTransfer


def run():
    org = Organization.objects.first()

    if not org:
        raise Exception("No organization found")

    Category.objects.filter(organization__isnull=True).update(organization=org)
    Supplier.objects.filter(organization__isnull=True).update(organization=org)
    Product.objects.filter(organization__isnull=True).update(organization=org)
    Location.objects.filter(organization__isnull=True).update(organization=org)

    StockItem.objects.filter(organization__isnull=True).update(organization=org)

    Order.objects.filter(organization__isnull=True).update(organization=org)
    OrderItem.objects.filter(organization__isnull=True).update(organization=org)

    StockMovement.objects.filter(organization__isnull=True).update(organization=org)
    StockTransfer.objects.filter(organization__isnull=True).update(organization=org)

    print("✅ Backfill completed")