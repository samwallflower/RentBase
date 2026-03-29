from django.test import TestCase
from apps.accounts.models import User
from apps.verification.models import UserVerification
from apps.verification.permissions import IsVerified
from unittest.mock import MagicMock


class VerificationTests(TestCase):
    def setUp(self):
        # Create a dummy user for the tests
        self.user = User.objects.create_user(
            username="kyctestuser",
            email="kyctest@rentbase.hu",
            password="Password123!"
        )

    def test_verification_record_auto_created(self):
        """Ensure a blank UserVerification is created when a User registers"""
        record_exists = UserVerification.objects.filter(user=self.user).exists()
        self.assertTrue(record_exists)

        # Check default status
        verification = UserVerification.objects.get(user=self.user)
        self.assertEqual(verification.status, 'not_started')

    def test_is_verified_permission_blocks_unverified_user(self):
        """Ensure our Bouncer (IsVerified) blocks unverified users"""
        permission = IsVerified()

        # Mock a web request
        request = MagicMock()
        request.user = self.user

        # WE REMOVED THE `request.user.is_authenticated = True` LINE!
        # Because self.user is a real user, it is already authenticated.

        # The permission should return False (Access Denied)
        has_access = permission.has_permission(request, None)
        self.assertFalse(has_access)