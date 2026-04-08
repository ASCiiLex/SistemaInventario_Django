import threading
import random

from django.db import connection

from inventory.tests_suite.base import BaseTestCase

from products.models import Product
from inventory.models.locations import Location
from inventory.models.stock import StockItem
from inventory.models.movements import StockMovement


class StressConcurrencyTest(BaseTestCase):

    def setUp(self):
        super().setUp()

        self.product = Product.objects.create(
            name="StressProduct",
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
            quantity=100
        )

    def test_high_concurrency_stress(self):

        errors = []

        def worker(thread_id):
            try:
                for _ in range(10):  # cada thread ejecuta varias ops
                    movement_type = random.choice(["IN", "OUT"])

                    qty = random.randint(1, 10)

                    if movement_type == "IN":
                        StockMovement(
                            organization=self.org,
                            product=self.product,
                            movement_type="IN",
                            destination=self.location,
                            quantity=qty
                        ).save()

                    else:
                        try:
                            StockMovement(
                                organization=self.org,
                                product=self.product,
                                movement_type="OUT",
                                origin=self.location,
                                quantity=qty
                            ).save()
                        except Exception:
                            # esperado si no hay stock suficiente
                            pass

            except Exception as e:
                errors.append((thread_id, str(e)))

            finally:
                connection.close()  # 🔥 crítico

        threads = []

        for i in range(10):  # 🔥 10 threads concurrentes
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 🔥 ASSERTS CRÍTICOS

        stock = StockItem.objects.get(
            product=self.product,
            location=self.location
        )

        # nunca negativo
        assert stock.quantity >= 0

        # consistencia global (no valores absurdos)
        assert stock.quantity <= 1000  # límite razonable

        # no errores inesperados
        assert len(errors) == 0, f"Errores en threads: {errors}"