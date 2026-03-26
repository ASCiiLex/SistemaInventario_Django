import random
from django.contrib.auth.models import User, Group
from categories.models import Category
from suppliers.models import Supplier
from products.models import Product
from inventory.models.locations import Location
from inventory.models.stock import StockItem
from inventory.models.movements import StockMovement
from inventory.models.orders import Order, OrderItem

from django.utils import timezone


def run():
    print("🔄 Generando datos...")

    # -------------------
    # USERS & GROUPS
    # -------------------
    group, _ = Group.objects.get_or_create(name="Managers")

    for i in range(5):
        user = User.objects.create_user(
            username=f"user{i}",
            password="1234",
            email=f"user{i}@test.com"
        )
        user.groups.add(group)

    # -------------------
    # CATEGORIES
    # -------------------
    categories = []
    for i in range(5):
        c = Category.objects.create(name=f"Categoria {i}")
        categories.append(c)

    # -------------------
    # SUPPLIERS
    # -------------------
    suppliers = []
    for i in range(5):
        s = Supplier.objects.create(name=f"Proveedor {i}")
        suppliers.append(s)

    # -------------------
    # LOCATIONS
    # -------------------
    locations = []
    for i in range(3):
        l = Location.objects.create(name=f"Almacen {i}")
        locations.append(l)

    # -------------------
    # PRODUCTS
    # -------------------
    products = []
    for i in range(50):
        p = Product.objects.create(
            name=f"Producto {i}",
            sku=f"SKU-{i}",
            category=random.choice(categories),
            supplier=random.choice(suppliers),
            stock=0,
            min_stock=10,
            cost_price=5,
            sale_price=10,
        )
        products.append(p)

    # -------------------
    # STOCK ITEMS
    # -------------------
    for p in products:
        for loc in locations:
            StockItem.objects.create(
                product=p,
                location=loc,
                quantity=random.randint(0, 100)
            )

    # -------------------
    # MOVEMENTS
    # -------------------
    for _ in range(100):
        p = random.choice(products)
        origin = random.choice(locations)
        destination = random.choice(locations)

        StockMovement.objects.create(
            product=p,
            movement_type=random.choice(["IN", "OUT", "TRANSFER"]),
            origin=origin,
            destination=destination,
            quantity=random.randint(1, 20),
        )

    # -------------------
    # ORDERS
    # -------------------
    for _ in range(20):
        order = Order.objects.create(
            supplier=random.choice(suppliers),
            location=random.choice(locations),
            status=random.choice(["pending", "sent", "received"]),
            created_at=timezone.now()
        )

        for _ in range(random.randint(1, 5)):
            OrderItem.objects.create(
                order=order,
                product=random.choice(products),
                quantity=random.randint(1, 10),
                cost_price=5
            )

    print("✅ Datos generados correctamente")