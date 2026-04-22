from django.contrib.auth.models import User
from organizations.models import Organization, Membership

from products.models import Product
from categories.models import Category
from suppliers.models import Supplier

from inventory.models import (
    Location,
    StockMovement,
    Order,
    OrderItem,
    StockTransfer,
    StockItem,
)


def run():
    print("🚀 Seed DEMO (determinista y consistente con dominio)")

    # =====================
    # USERS
    # =====================
    def create_user(username):
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password("demo1234")
            user.save()
        return user

    admin = create_user("demo_admin")
    manager = create_user("demo_manager")
    staff = create_user("demo_staff")

    # =====================
    # ORGANIZATION
    # =====================
    org, _ = Organization.objects.get_or_create(
        slug="demo",
        defaults={
            "name": "Demo Corp",
            "owner": admin,
        }
    )

    Membership.objects.get_or_create(
        user=admin,
        organization=org,
        defaults={"role": Membership.Roles.OWNER}
    )

    Membership.objects.get_or_create(
        user=manager,
        organization=org,
        defaults={"role": Membership.Roles.MANAGER}
    )

    Membership.objects.get_or_create(
        user=staff,
        organization=org,
        defaults={"role": Membership.Roles.STAFF}
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
                "min_stock": 5,
            }
        )
        products.append(p)

    # =====================
    # STOCK INICIAL (solo IN)
    # =====================
    for p in products:
        for loc in locations:
            try:
                StockMovement(
                    organization=org,
                    product=p,
                    movement_type="IN",
                    source_type="manual",
                    destination=loc,
                    quantity=30,
                    note="Stock inicial demo",
                ).save()
            except:
                continue

    # =====================
    # OUT (válido)
    # =====================
    for i in range(20):
        p = products[i % len(products)]
        loc = locations[i % len(locations)]

        try:
            StockMovement(
                organization=org,
                product=p,
                movement_type="OUT",
                source_type="manual",
                origin=loc,
                quantity=2,
            ).save()
        except:
            continue

    # =====================
    # TRANSFERS (CORRECTO)
    # =====================
    for i in range(10):
        p = products[i % len(products)]
        origin = locations[i % len(locations)]
        destination = locations[(i + 1) % len(locations)]

        transfer = StockTransfer.objects.create(
            organization=org,
            product=p,
            origin=origin,
            destination=destination,
            quantity=2,
            created_by=admin,
        )

        try:
            transfer.confirm(admin)
        except:
            continue

    # =====================
    # ORDERS
    # =====================
    for i in range(3):
        order = Order.objects.create(
            organization=org,
            supplier=suppliers[i % len(suppliers)],
            location=locations[i % len(locations)],
        )

        items = []

        for j in range(2):
            product = products[(i + j) % len(products)]
            qty = 5

            OrderItem.objects.create(
                organization=org,
                order=order,
                product=product,
                quantity=qty,
                cost_price=product.cost_price,
            )

            items.append({
                "product": product,
                "quantity": qty
            })

        try:
            order.mark_as_sent(admin)
            order.receive_items(admin, items)
        except:
            continue

    print("✅ Seed DEMO limpio y consistente")