from inventory.tests_suite.base import BaseTestCase

from products.models import Product
from inventory.models.locations import Location
from inventory.models.orders import Order, OrderItem
from inventory.models.stock import StockItem


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
            location=self.location
        )

        self.order.status = "sent"
        self.order.save()

        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=10,
            cost_price=1
        )

    def test_order_partial_receive(self):
        self.order.receive_items(self.user, [
            {
                "product": self.product,
                "quantity": 5
            }
        ])

        # 🔥 VALIDAMOS EFECTO REAL → STOCK
        stock = StockItem.objects.get(
            product=self.product,
            location=self.location
        )

        assert stock.quantity == 5