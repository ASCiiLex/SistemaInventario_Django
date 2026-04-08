from inventory.tests_suite.base import BaseTestCase

from products.models import Product
from inventory.models.locations import Location
from inventory.models.movements import StockMovement


class IdempotencyTest(BaseTestCase):

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

    def test_same_key_not_duplicated(self):
        key = "test-key"

        m1 = StockMovement(
            organization=self.org,
            product=self.product,
            movement_type="IN",
            destination=self.location,
            quantity=10,
            idempotency_key=key
        )
        m1.save()

        m2 = StockMovement(
            organization=self.org,
            product=self.product,
            movement_type="IN",
            destination=self.location,
            quantity=10,
            idempotency_key=key
        )
        m2.save()

        assert StockMovement.objects.count() == 1