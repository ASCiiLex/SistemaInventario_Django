from unittest.mock import patch

from django.db import transaction

from inventory.tests_suite.base import BaseTestCase

from products.models import Product
from inventory.models.locations import Location
from inventory.models.stock import StockItem
from inventory.models.movements import StockMovement


class FailureInjectionTest(BaseTestCase):

    def setUp(self):
        super().setUp()

        self.product = Product.objects.create(
            name="FailureProduct",
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

    def test_failure_during_stock_update_rolls_back(self):

        initial_stock = StockItem.objects.get(
            product=self.product,
            location=self.location
        ).quantity

        def crash_apply_stock(*args, **kwargs):
            raise Exception("Injected failure inside _apply_stock")

        with patch(
            "inventory.services.stock_domain.StockDomainService._apply_stock",
            side_effect=crash_apply_stock
        ):
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

        stock = StockItem.objects.get(
            product=self.product,
            location=self.location
        )

        # 🔥 no debe haber cambiado nada
        assert stock.quantity == initial_stock

    def test_failure_after_movement_creation_rolls_back(self):

        initial_count = StockMovement.objects.count()

        def crash_after_save(*args, **kwargs):
            raise Exception("Injected failure after save")

        with patch(
            "inventory.services.stock_domain.StockDomainService._validate_global_stock",
            side_effect=crash_after_save
        ):
            try:
                StockMovement(
                    organization=self.org,
                    product=self.product,
                    movement_type="IN",
                    destination=self.location,
                    quantity=10
                ).save()
            except Exception:
                pass

        # 🔥 no debe haberse persistido el movimiento
        assert StockMovement.objects.count() == initial_count