from inventory.tests_suite.base import BaseTestCase

from products.models import Product
from inventory.models.locations import Location
from inventory.models.stock import StockItem
from inventory.models.transfers import StockTransfer


class DoubleClickTest(BaseTestCase):

    def setUp(self):
        super().setUp()

        self.product = Product.objects.create(
            name="TestProduct",
            organization=self.org
        )

        self.origin = Location.objects.create(
            name="A",
            organization=self.org
        )

        self.dest = Location.objects.create(
            name="B",
            organization=self.org
        )

        # ✅ FIX: stock inicial necesario
        StockItem.objects.create(
            organization=self.org,
            product=self.product,
            location=self.origin,
            quantity=20
        )

        self.transfer = StockTransfer.objects.create(
            organization=self.org,
            product=self.product,
            origin=self.origin,
            destination=self.dest,
            quantity=10,
            created_by=self.user
        )

    def test_double_confirm_transfer(self):
        self.transfer.confirm(self.user)
        self.transfer.confirm(self.user)

        self.transfer.refresh_from_db()

        assert self.transfer.status == "received"