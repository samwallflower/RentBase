from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import MagicMock
from apps.accounts.models import User
from .models import UserVerification
from .permissions import IsVerified


class VerificationV4Tests(APITestCase):
    def setUp(self):
        # Create a dummy user
        self.user = User.objects.create_user(
            username="kyctestuser",
            email="kyctest@rentbase.hu",
            password="Password123!"
        )
        self.client.force_authenticate(user=self.user)
        self.start_url = reverse('start_verification')

    def test_verification_record_auto_created(self):
        """Ensure a blank UserVerification is created when a User registers"""
        record_exists = UserVerification.objects.filter(user=self.user).exists()
        self.assertTrue(record_exists)

        verification = UserVerification.objects.get(user=self.user)
        self.assertEqual(verification.status, 'not_started')

        # Architecture Check: Ensure PII fields do NOT exist (v4.0 compliance)
        self.assertFalse(hasattr(verification, 'legal_first_name'))
        self.assertFalse(hasattr(verification, 'id_document_number'))

    def test_is_verified_permission_blocks_unverified_user(self):
        """Ensure our Bouncer (IsVerified) blocks unverified users"""
        permission = IsVerified()

        request = MagicMock()
        request.user = self.user

        # User is 'unverified' by default, should return False
        has_access = permission.has_permission(request, None)
        self.assertFalse(has_access)

    def test_start_verification_requires_tos(self):
        """Ensure the API rejects requests that don't accept the Terms of Service"""
        response = self.client.post(self.start_url, {"tos_accepted": False})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    # Force Stripe key to be empty to trigger Dev Mode
    @override_settings(STRIPE_SECRET_KEY='')
    def test_dev_mode_auto_verification(self):
        """Ensure Dev Mode instantly verifies the user without hitting Stripe"""
        response = self.client.post(self.start_url, {"tos_accepted": True})

        # Should succeed and return the dev mode flag
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['client_secret'], "dev_mode_auto_verified")

        # Check database updates
        self.user.refresh_from_db()
        self.assertEqual(self.user.userprofile.verification_status, 'verified')
        self.assertEqual(self.user.userverification.status, 'verified')
        self.assertIsNotNone(self.user.userverification.tos_accepted_at)