from django.contrib.auth.models import User
from organizations.models import Organization, Membership

from products.models import Product
from categories.models import Category
from suppliers.models import Supplier

from inventory.models import Location, StockMovement


def run():
    print("🚀 Seed DEMO (autosuficiente, rápido y consistente)")

    # =====================
    # USERS (idempotente)
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
    for i in range(10):
        p, _ = Product.objects.get_or_create(
            sku=f"DEMO-SKU-{i}",
            organization=org,
            defaults={
                "name": f"Producto Demo {i}",
                "category": categories[i % 3],
                "supplier": suppliers[i % 3],
                "cost_price": 10 + i,
                "sale_price": 30 + i * 2,
                "min_stock": 5 if i < 8 else 25,  # 🔥 algunos forzados a bajo stock
            },
        )
        products.append(p)

    # =====================
    # STOCK INICIAL
    # =====================
    for p in products:
        for loc in locations:
            StockMovement.objects.create(
                organization=org,
                product=p,
                movement_type="IN",
                source_type="manual",
                destination=loc,
                quantity=20,
            )

    # =====================
    # SALIDAS CONTROLADAS (generan alertas)
    # =====================
    for i, p in enumerate(products):
        loc = locations[i % len(locations)]

        qty = 15 if i >= 8 else 5  # 🔥 últimos productos caerán bajo mínimo

        StockMovement.objects.create(
            organization=org,
            product=p,
            movement_type="OUT",
            source_type="manual",
            origin=loc,
            quantity=qty,
        )

    print("✅ Seed DEMO completo")