from django.core.exceptions import ValidationError
from django.test import TransactionTestCase

from inventory.tests_suite.base import BaseTestCase

from products.models import Product
from inventory.models.locations import Location
from inventory.models.movements import StockMovement


class NegativeStockTest(TransactionTestCase, BaseTestCase):

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

    def test_no_negative_stock(self):
        movement = StockMovement(
            organization=self.org,
            product=self.product,
            movement_type="OUT",
            origin=self.location,
            quantity=10,
        )

        try:
            movement.save()
            assert False, "Should have failed"
        except ValidationError:
            assert True