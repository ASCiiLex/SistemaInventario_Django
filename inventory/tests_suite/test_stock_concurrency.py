import threading
from django.test import TransactionTestCase

from inventory.tests_suite.base import BaseTestCase

from products.models import Product
from inventory.models.locations import Location
from inventory.models.stock import StockItem
from inventory.models.movements import StockMovement


class StockConcurrencyTest(TransactionTestCase, BaseTestCase):

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

    def test_parallel_out_movements_only_one_succeeds(self):

        results = []

        def do_movement():
            try:
                m = StockMovement(
                    organization=self.org,
                    product=self.product,
                    movement_type="OUT",
                    origin=self.location,
                    quantity=10
                )
                m.save()
                results.append("success")
            except Exception:
                results.append("fail")

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

        # 🔥 Solo uno debe ejecutarse correctamente
        assert results.count("success") == 1

        # 🔥 Stock consistente
        assert stock.quantity == 0