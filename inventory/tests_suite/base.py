from django.test import TestCase
from django.contrib.auth.models import User

from organizations.models import Organization


class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            password="test123"
        )

        self.org = Organization.objects.create(
            name="TestOrg",
            owner=self.user
        )