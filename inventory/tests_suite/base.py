from django.test import TransactionTestCase
from django.contrib.auth.models import User

from organizations.models import Organization


class BaseTestDataMixin:
    def setup_base_data(self):
        self.user = User.objects.create_user(
            username="test_user",
            password="test123"
        )

        self.org = Organization.objects.create(
            name="TestOrg",
            owner=self.user
        )


class BaseTestCase(TransactionTestCase, BaseTestDataMixin):
    reset_sequences = True

    def setUp(self):
        self.setup_base_data()