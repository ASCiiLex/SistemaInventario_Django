from django.contrib.auth.models import User
from organizations.models import Organization, Membership

from products.models import Product
from categories.models import Category
from suppliers.models import Supplier

from inventory.models import Location
from inventory.models.stock import StockItem
from inventory.models import StockMovement

from django.utils import timezone
from random import randint, choice


def run():
    print("🚀 Seed DEMO (escenario realista con alertas y actividad)")

    # =====================
    # USERS
    # =====================
    admin, _ = User.objects.get_or_create(
        username="admin",
        defaults={"email": "admin@demo.com", "is_staff": True, "is_superuser": True},
    )
    admin.set_password("admin1234")
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    manager, _ = User.objects.get_or_create(username="demo_manager")
    manager.set_password("demo1234")
    manager.save()

    staff, _ = User.objects.get_or_create(username="demo_staff")
    staff.set_password("demo1234")
    staff.save()

    # =====================
    # ORGANIZATION
    # =====================
    org, _ = Organization.objects.get_or_create(
        slug="demo",
        defaults={"name": "Demo Corp", "owner": admin},
    )

    if not org.owner:
        org.owner = admin
        org.save()

    Membership.objects.get_or_create(
        user=admin, organization=org, defaults={"role": Membership.Roles.OWNER}
    )
    Membership.objects.get_or_create(
        user=manager, organization=org, defaults={"role": Membership.Roles.MANAGER}
    )
    Membership.objects.get_or_create(
        user=staff, organization=org, defaults={"role": Membership.Roles.STAFF}
    )

    # =====================
    # BASE DATA
    # =====================
    categories = [
        Category.objects.get_or_create(name=n, organization=org)[0]
        for n in ["Electrónica", "Ropa", "Hogar"]
    ]

    suppliers = [
        Supplier.objects.get_or_create(name=n, organization=org)[0]
        for n in ["Amazon", "Ikea", "Zara"]
    ]

    locations = [
        Location.objects.get_or_create(name=n, organization=org)[0]
        for n in ["Madrid", "Barcelona", "Valencia"]
    ]

    # =====================
    # PRODUCTS
    # =====================
    products = []
    for i in range(12):
        p, _ = Product.objects.get_or_create(
            sku=f"DEMO-SKU-{i}",
            organization=org,
            defaults={
                "name": f"Producto Demo {i}",
                "category": categories[i % 3],
                "supplier": suppliers[i % 3],
                "cost_price": 10 + i,
                "sale_price": 30 + i * 2,
                "min_stock": 8 if i < 8 else 20,
            },
        )
        products.append(p)

    # =====================
    # STOCK
    # =====================
    stock_items = []

    for p in products:
        for loc in locations:
            stock_items.append(
                StockItem(
                    organization=org,
                    product=p,
                    location=loc,
                    quantity=40,
                    min_stock=p.min_stock,
                )
            )

    StockItem.objects.bulk_create(stock_items, ignore_conflicts=True)

    # =====================
    # ESTADOS
    # =====================

    for p in products[:6]:
        StockItem.objects.filter(product=p, organization=org).update(quantity=30)

    for p in products[6:10]:
        StockItem.objects.filter(product=p, organization=org).update(quantity=5)

    for p in products[8:12]:
        StockItem.objects.filter(product=p, organization=org).update(quantity=10)

    # =====================
    # 🔥 MOVIMIENTOS (CORREGIDO)
    # =====================
    print("📦 Generando movimientos de stock...")

    movement_types = ["IN", "OUT", "TRANSFER"]

    movements = []

    stock_items = StockItem.objects.select_related("product", "organization")

    for item in stock_items:
        for _ in range(randint(1, 3)):
            movements.append(
                StockMovement(
                    organization=item.organization,
                    product=item.product,
                    quantity=randint(1, 10),
                    movement_type=choice(movement_types),
                    created_at=timezone.now(),
                )
            )

    StockMovement.objects.bulk_create(movements, ignore_conflicts=True)

    print(f"✔ Movimientos creados: {len(movements)}")
    print("✅ Seed DEMO listo (correcto y consistente)")