import random
from django.contrib.auth.models import User, Group
from django.utils import timezone

from products.models import Product
from categories.models import Category
from suppliers.models import Supplier
from inventory.models import Location, StockItem, StockMovement, Order, OrderItem


def run():
    print("🔄 Generando datos PRO...")

    # -------------------
    # USERS & GROUPS
    # -------------------
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    user_group, _ = Group.objects.get_or_create(name="Usuario")

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@test.com", "admin1234")

    users = []
    for i in range(3):
        u, _ = User.objects.get_or_create(username=f"user{i}")
        u.set_password("1234")
        u.save()
        u.groups.add(user_group)
        users.append(u)

    # -------------------
    # CATEGORIES & SUPPLIERS
    # -------------------
    categories = []
    for name in ["Electrónica", "Ropa", "Hogar"]:
        c, _ = Category.objects.get_or_create(name=name)
        categories.append(c)

    suppliers = []
    for name in ["Amazon", "Ikea", "Zara"]:
        s, _ = Supplier.objects.get_or_create(name=name)
        suppliers.append(s)

    # -------------------
    # LOCATIONS
    # -------------------
    locations = []
    for name in ["Madrid", "Barcelona", "Valencia"]:
        loc, _ = Location.objects.get_or_create(name=name)
        locations.append(loc)

    # -------------------
    # PRODUCTS
    # -------------------
    products = []
    for i in range(20):
        p, _ = Product.objects.get_or_create(
            sku=f"SKU{i}",
            defaults={
                "name": f"Producto {i}",
                "category": random.choice(categories),
                "supplier": random.choice(suppliers),
                "min_stock": 0,  # 🔥 DEPRECATED
                "cost_price": random.uniform(5, 50),
                "sale_price": random.uniform(60, 120),
            }
        )
        products.append(p)

    # -------------------
    # STOCK INICIAL + MIN_STOCK POR ALMACÉN
    # -------------------
    for p in products:
        for loc in locations:

            qty = random.randint(10, 50)

            # 🔥 mínimo por almacén (clave del nuevo modelo)
            min_stock = random.randint(5, 15)

            stock_item, _ = StockItem.objects.get_or_create(
                product=p,
                location=loc,
                defaults={
                    "quantity": 0,
                    "min_stock": min_stock,
                }
            )

            # si ya existía (reseed), actualizar mínimo
            stock_item.min_stock = min_stock
            stock_item.save()

            # movimiento inicial
            StockMovement.objects.create(
                product=p,
                movement_type="IN",
                destination=loc,
                quantity=qty,
                note="Stock inicial",
            )

    # -------------------
    # MOVIMIENTOS REALISTAS
    # -------------------
    for _ in range(200):
        p = random.choice(products)
        movement_type = random.choice(["OUT", "TRANSFER"])

        if movement_type == "OUT":
            origin = random.choice(locations)

            stock = StockItem.objects.filter(product=p, location=origin).first()
            if not stock or stock.quantity <= 1:
                continue

            qty = random.randint(1, stock.quantity)

            StockMovement.objects.create(
                product=p,
                movement_type="OUT",
                origin=origin,
                quantity=qty,
            )

        elif movement_type == "TRANSFER":
            origin, destination = random.sample(locations, 2)

            stock = StockItem.objects.filter(product=p, location=origin).first()
            if not stock or stock.quantity <= 1:
                continue

            qty = random.randint(1, stock.quantity)

            StockMovement.objects.create(
                product=p,
                movement_type="TRANSFER",
                origin=origin,
                destination=destination,
                quantity=qty,
            )

    # -------------------
    # ORDERS
    # -------------------
    for _ in range(10):
        order = Order.objects.create(
            supplier=random.choice(suppliers),
            location=random.choice(locations),
            status=random.choice(["pending", "sent", "received"]),
            created_at=timezone.now(),
        )

        for _ in range(random.randint(1, 5)):
            OrderItem.objects.create(
                order=order,
                product=random.choice(products),
                quantity=random.randint(1, 10),
                cost_price=random.uniform(5, 50),
            )

    print("✅ Seed PRO completado (modelo nuevo)")