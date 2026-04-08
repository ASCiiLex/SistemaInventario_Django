from django.test import TestCase

from inventory.tests_suite.base import BaseTestDataMixin

from products.models import Product
from inventory.models.locations import Location
from inventory.models.orders import Order, OrderItem
from inventory.models.stock import StockItem


class OrderTest(BaseTestDataMixin, TestCase):

    def setUp(self):
        super().setUp()

        self.product = Product.objects.create(
            name="TestProduct",
            organization=self.org
        )

        self.location = Location.objects.create(
            name="Main",
            organization=self.org
        )

        self.order = Order.objects.create(
            organization=self.org
        )

        # 🔥 FIX: añadir cost_price obligatorio
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=10,
            cost_price=5  # 👈 clave
        )

    def test_order_partial_receive(self):

        self.order.receive_items(self.user, [
            {
                "order_item": self.order_item,
                "quantity": 5
            }
        ])

        stock = StockItem.objects.get(
            product=self.product,
            location=self.location
        )

        assert stock.quantity == 5