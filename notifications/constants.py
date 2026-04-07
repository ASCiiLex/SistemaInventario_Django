"""
🔥 EVENTOS CENTRALIZADOS (SOURCE OF TRUTH)

- Evita strings mágicos
- Unifica backend + frontend
- Escalable SaaS
"""


class Events:
    # INVENTORY
    STOCK_LOW = "inventory:stock_low"
    STOCK_CHANGED = "inventory:stock_changed"
    MOVEMENT_CREATED = "inventory:movement_created"
    PRODUCT_RISK = "inventory:product_risk"

    # ORDERS
    ORDERS_UPDATED = "orders:updated"

    # NOTIFICATIONS
    NOTIFICATIONS_UPDATED = "inventory:notifications_updated"