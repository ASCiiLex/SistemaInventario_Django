import random
from django.contrib.auth.models import User
from django.utils import timezone

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
)

from notifications.models import Notification, UserNotification


def get_or_create_org(model, org, **kwargs):
    return model.objects.get_or_create(
        organization=org,
        **kwargs
    )[0]


def run():
    print("🔄 Seed PRO (multi-tenant + dominio real + auditoría)")

    # =====================
    # USERS
    # =====================
    admin, _ = User.objects.get_or_create(username="alex")
    admin.set_password("admin123")
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()

    users = []
    roles = [
        Membership.Roles.ADMIN,
        Membership.Roles.MANAGER,
        Membership.Roles.STAFF,
    ]

    for i in range(3):
        u, _ = User.objects.get_or_create(username=f"user{i}")
        u.set_password("1234")
        u.save()
        users.append(u)

    all_users = [admin] + users

    # =====================
    # ORGANIZATION
    # =====================
    org, _ = Organization.objects.get_or_create(
        slug="default",
        defaults={
            "name": "Default Organization",
            "owner": admin,
        }
    )

    if not org.owner:
        org.owner = admin
        org.save()

    Membership.objects.get_or_create(
        user=admin,
        organization=org,
        defaults={"role": Membership.Roles.OWNER}
    )

    for i, u in enumerate(users):
        Membership.objects.get_or_create(
            user=u,
            organization=org,
            defaults={"role": roles[i % len(roles)]}
        )

    # =====================
    # CATEGORIES & SUPPLIERS (🔥 FIX multi-tenant)
    # =====================
    categories = [
        get_or_create_org(Category, org, name=n)
        for n in ["Electrónica", "Ropa", "Hogar"]
    ]

    suppliers = [
        get_or_create_org(Supplier, org, name=n)
        for n in ["Amazon", "Ikea", "Zara"]
    ]

    # =====================
    # LOCATIONS
    # =====================
    locations = [
        get_or_create_org(Location, org, name=n)
        for n in ["Madrid", "Barcelona", "Valencia"]
    ]

    # =====================
    # PRODUCTS
    # =====================
    products = []
    for i in range(20):
        p, _ = Product.objects.get_or_create(
            sku=f"SKU{i}",
            organization=org,
            defaults={
                "name": f"Producto {i}",
                "category": random.choice(categories),
                "supplier": random.choice(suppliers),
                "min_stock": 5,
                "cost_price": random.uniform(5, 50),
                "sale_price": random.uniform(60, 120),
            }
        )
        products.append(p)

    # =====================
    # STOCK INICIAL (DOMINIO REAL)
    # =====================
    for p in products:
        for loc in locations:
            try:
                StockMovement(
                    organization=org,
                    product=p,
                    movement_type="IN",
                    destination=loc,
                    quantity=random.randint(10, 50),
                    note="Stock inicial",
                ).save()
            except:
                continue

    # =====================
    # MOVIMIENTOS
    # =====================
    for _ in range(200):
        p = random.choice(products)

        if random.choice(["OUT", "TRANSFER"]) == "OUT":
            origin = random.choice(locations)

            try:
                StockMovement(
                    organization=org,
                    product=p,
                    movement_type="OUT",
                    origin=origin,
                    quantity=random.randint(1, 5),
                ).save()
            except:
                continue
        else:
            origin, destination = random.sample(locations, 2)

            try:
                StockMovement(
                    organization=org,
                    product=p,
                    movement_type="TRANSFER",
                    origin=origin,
                    destination=destination,
                    quantity=random.randint(1, 5),
                ).save()
            except:
                continue

    # =====================
    # ORDERS (FLUJO REAL)
    # =====================
    for _ in range(10):
        user = random.choice(all_users)

        order = Order.objects.create(
            organization=org,
            supplier=random.choice(suppliers),
            location=random.choice(locations),
        )

        items = []

        for _ in range(random.randint(1, 5)):
            product = random.choice(products)
            qty = random.randint(1, 10)

            OrderItem.objects.create(
                organization=org,
                order=order,
                product=product,
                quantity=qty,
                cost_price=random.uniform(5, 50),
            )

            items.append({
                "product": product,
                "quantity": qty
            })

        try:
            order.mark_as_sent(user)
            order.receive_items(user, items)
        except:
            continue

    # =====================
    # TRANSFERS (FLUJO REAL)
    # =====================
    for _ in range(20):
        user = random.choice(all_users)
        product = random.choice(products)
        origin, destination = random.sample(locations, 2)

        transfer = StockTransfer.objects.create(
            organization=org,
            product=product,
            origin=origin,
            destination=destination,
            quantity=random.randint(1, 5),
            created_by=user,
        )

        try:
            transfer.confirm(user)
        except:
            continue

    # =====================
    # NOTIFICATIONS
    # =====================
    for _ in range(30):
        product = random.choice(products)

        notif = Notification.objects.create(
            organization=org,
            product=product,
            type=random.choice(["stock_item_low", "product_risk", "order"]),
            priority=random.choice(["critical", "warning", "info"]),
            message=f"Alerta en {product.name}",
        )

        for user in all_users:
            UserNotification.objects.get_or_create(
                user=user,
                notification=notif,
                defaults={"seen": random.choice([True, False])}
            )

    print("✅ Seed completo (auditoría incluida)")