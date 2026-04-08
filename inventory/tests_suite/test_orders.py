from inventory.tests_suite.base import BaseTestCase

from products.models import Product
from inventory.models.locations import Location
from inventory.models.orders import Order, OrderItem


class OrderTest(BaseTestCase):

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
            organization=self.org,
            location=self.location,
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=10,
            cost_price=5,
            organization=self.org
        )

    def test_order_partial_receive(self):
        self.order.mark_as_sent(self.user)

        self.order.receive_items(self.user, [
            {"product": self.product, "quantity": 5}
        ])

        self.order.refresh_from_db()

        assert self.order.status == "partially_received"