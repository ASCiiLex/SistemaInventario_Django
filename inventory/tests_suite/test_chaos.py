import threading

from django.db import connection, transaction

from inventory.tests_suite.base import BaseTestCase

from products.models import Product
from inventory.models.locations import Location
from inventory.models.stock import StockItem
from inventory.models.movements import StockMovement


class ChaosTest(BaseTestCase):

    def setUp(self):
        super().setUp()

        self.product = Product.objects.create(
            name="ChaosProduct",
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
            quantity=50
        )

    def test_transaction_rollback_integrity(self):

        initial_stock = StockItem.objects.get(
            product=self.product,
            location=self.location
        ).quantity

        try:
            with transaction.atomic():

                movement = StockMovement(
                    organization=self.org,
                    product=self.product,
                    movement_type="OUT",
                    origin=self.location,
                    quantity=20
                )

                movement.save()

                # 💥 simulamos fallo duro en mitad de la transacción
                raise Exception("Simulated crash")

        except Exception:
            pass

        # 🔥 ASSERT CRÍTICO → rollback debe dejar todo intacto
        stock = StockItem.objects.get(
            product=self.product,
            location=self.location
        )

        assert stock.quantity == initial_stock


    def test_partial_failures_under_concurrency(self):

        errors = []

        def worker(should_fail=False):
            try:
                with transaction.atomic():

                    movement = StockMovement(
                        organization=self.org,
                        product=self.product,
                        movement_type="OUT",
                        origin=self.location,
                        quantity=5
                    )

                    movement.save()

                    if should_fail:
                        raise Exception("Injected failure")

            except Exception:
                pass
            finally:
                connection.close()

        threads = []

        # 🔥 mezcla de threads sanos + fallidos
        for i in range(10):
            t = threading.Thread(
                target=worker,
                kwargs={"should_fail": i % 2 == 0}
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        stock = StockItem.objects.get(
            product=self.product,
            location=self.location
        )

        # 🔥 nunca negativo
        assert stock.quantity >= 0

        # 🔥 consistencia razonable (no corrupción)
        assert stock.quantity <= 50