from django.contrib.auth.models import User
from organizations.models import Organization, Membership

from products.models import Product
from categories.models import Category
from suppliers.models import Supplier
from inventory.models import Location


def run():
    print("⚡ Seed BASE (rápido y mínimo)")

    # SUPERUSER
    admin, _ = User.objects.get_or_create(username="admin")
    admin.set_password("admin1234")
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()

    # USERS
    manager, _ = User.objects.get_or_create(username="demo_manager")
    manager.set_password("demo1234")
    manager.save()

    staff, _ = User.objects.get_or_create(username="demo_staff")
    staff.set_password("demo1234")
    staff.save()

    # ORGANIZATION
    org, _ = Organization.objects.get_or_create(
        slug="demo",
        defaults={
            "name": "Demo Corp",
            "owner": admin,
        }
    )

    Membership.objects.get_or_create(user=admin, organization=org, defaults={"role": Membership.Roles.OWNER})
    Membership.objects.get_or_create(user=manager, organization=org, defaults={"role": Membership.Roles.MANAGER})
    Membership.objects.get_or_create(user=staff, organization=org, defaults={"role": Membership.Roles.STAFF})

    # BASE DATA
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

    # PRODUCTS
    for i in range(10):
        Product.objects.get_or_create(
            sku=f"BASE-SKU-{i}",
            organization=org,
            defaults={
                "name": f"Producto Base {i}",
                "category": categories[i % 3],
                "supplier": suppliers[i % 3],
                "cost_price": 10 + i,
                "sale_price": 30 + i,
                "min_stock": 5,
            }
        )

    print("✅ Seed BASE completo")