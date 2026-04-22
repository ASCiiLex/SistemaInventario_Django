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
    print("🚀 Seed DEMO (determinista y no destructivo)")

    # =====================
    # USERS (NO sobrescribe)
    # =====================
    def create_user(username, role):
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password("demo1234")
            user.save()
        return user

    admin = create_user("demo_admin", Membership.Roles.ADMIN)
    manager = create_user("demo_manager", Membership.Roles.MANAGER)
    staff = create_user("demo_staff", Membership.Roles.STAFF)

    users = [admin, manager, staff]

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

    if not org.owner:
        org.owner = admin
        org.save()

    # memberships
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
    # CATEGORIES
    # =====================
    cat_names = ["Electrónica", "Ropa", "Hogar"]
    categories = [
        Category.objects.get_or_create(name=n, organization=org)[0]
        for n in cat_names
    ]

    # =====================
    # SUPPLIERS
    # =====================
    supplier_names = ["Amazon", "Ikea", "Zara"]
    suppliers = [
        Supplier.objects.get_or_create(name=n, organization=org)[0]
        for n in supplier_names
    ]

    # =====================
    # LOCATIONS
    # =====================
    loc_names = ["Madrid", "Barcelona", "Valencia"]
    locations = [
        Location.objects.get_or_create(name=n, organization=org)[0]
        for n in loc_names
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
                "category": categories[i % len(categories)],
                "supplier": suppliers[i % len(suppliers)],
                "cost_price": 10 + i,
                "sale_price": 30 + i * 2,
            }
        )
        products.append(p)

    # =====================
    # STOCK INICIAL
    # =====================
    for i, p in enumerate(products):
        for j, loc in enumerate(locations):

            qty = 20 + (i * 3) - (j * 5)
            if qty < 0:
                qty = 5

            movement = StockMovement(
                organization=org,
                product=p,
                movement_type="IN",
                destination=loc,
                quantity=qty,
                note="Stock inicial demo",
            )
            movement.save()

            item = StockItem.objects.get(
                organization=org,
                product=p,
                location=loc
            )

            # algunos con low stock
            item.min_stock = 15 if i % 3 == 0 else 5
            item.save(update_fields=["min_stock"])

    # =====================
    # MOVIMIENTOS
    # =====================
    for i in range(40):
        p = products[i % len(products)]

        if i % 3 == 0:
            # OUT
            loc = locations[i % len(locations)]
            try:
                StockMovement(
                    organization=org,
                    product=p,
                    movement_type="OUT",
                    origin=loc,
                    quantity=2 + (i % 3),
                ).save()
            except:
                continue

        else:
            # TRANSFER
            origin = locations[i % len(locations)]
            destination = locations[(i + 1) % len(locations)]

            try:
                StockMovement(
                    organization=org,
                    product=p,
                    movement_type="TRANSFER",
                    origin=origin,
                    destination=destination,
                    quantity=1 + (i % 2),
                ).save()
            except:
                continue

    # =====================
    # ORDERS
    # =====================
    for i in range(5):
        order = Order.objects.create(
            organization=org,
            supplier=suppliers[i % len(suppliers)],
            location=locations[i % len(locations)],
        )

        items = []

        for j in range(3):
            product = products[(i + j) % len(products)]
            qty = 5 + j

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

    # =====================
    # TRANSFERS
    # =====================
    for i in range(10):
        product = products[i % len(products)]
        origin = locations[i % len(locations)]
        destination = locations[(i + 1) % len(locations)]

        transfer = StockTransfer.objects.create(
            organization=org,
            product=product,
            origin=origin,
            destination=destination,
            quantity=2,
            created_by=admin,
        )

        try:
            transfer.confirm(admin)
        except:
            continue

    print("✅ Seed DEMO completado")