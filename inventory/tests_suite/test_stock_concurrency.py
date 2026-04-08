import threading

from django.test import TransactionTestCase

from inventory.tests_suite.base import BaseTestDataMixin

from products.models import Product
from inventory.models.locations import Location
from inventory.models.stock import StockItem
from inventory.models.movements import StockMovement


class StockConcurrencyTest(BaseTestDataMixin, TransactionTestCase):

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

        StockItem.objects.create(
            organization=self.org,
            product=self.product,
            location=self.location,
            quantity=10
        )

    def test_parallel_out_movements(self):

        def do_movement():
            try:
                StockMovement(
                    organization=self.org,
                    product=self.product,
                    movement_type="OUT",
                    origin=self.location,
                    quantity=10
                ).save()
            except Exception:
                pass

        t1 = threading.Thread(target=do_movement)
        t2 = threading.Thread(target=do_movement)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        stock = StockItem.objects.get(
            product=self.product,
            location=self.location
        )

        assert stock.quantity >= 0