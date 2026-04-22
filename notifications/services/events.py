from notifications.events import register_event
from notifications.constants import Events
from .core import create_notification


@register_event(Events.STOCK_LOW)
def handle_stock_low(payload: dict):
    create_notification(
        product=payload.get("product"),
        location=payload.get("location"),
        type_=Events.STOCK_LOW,
    )


@register_event(Events.PRODUCT_RISK)
def handle_product_risk(payload: dict):
    create_notification(
        product=payload.get("product"),
        type_=Events.PRODUCT_RISK,
    )