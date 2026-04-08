from django.test import TransactionTestCase
from django.contrib.auth.models import User

from organizations.models import Organization


class BaseTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            password="test123"
        )

        self.org = Organization.objects.create(
            name="TestOrg",
            owner=self.user
        )