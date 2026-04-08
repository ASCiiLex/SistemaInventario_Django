import threading
from django.test import TransactionTestCase

from inventory.tests_suite.base import BaseTestCase

from products.models import Product
from inventory.models.locations import Location
from inventory.models.movements import StockMovement
from inventory.models.stock import StockItem


class IdempotencyTest(TransactionTestCase, BaseTestCase):

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

    def test_same_key_not_duplicated_concurrent(self):
        key = "test-key"

        def create_movement():
            try:
                StockMovement(
                    organization=self.org,
                    product=self.product,
                    movement_type="IN",
                    destination=self.location,
                    quantity=10,
                    idempotency_key=key
                ).save()
            except Exception:
                pass

        t1 = threading.Thread(target=create_movement)
        t2 = threading.Thread(target=create_movement)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        movements = StockMovement.objects.all()
        stock = StockItem.objects.get(
            product=self.product,
            location=self.location
        )

        # 🔥 Solo un movimiento
        assert movements.count() == 1

        # 🔥 Stock consistente
        assert stock.quantity == 10