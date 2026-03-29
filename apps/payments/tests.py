from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from apps.accounts.models import User
from apps.listings.models import Item
from apps.bookings.models import Booking
from .models import Payment, DepositHold


class PaymentTests(APITestCase):
    def setUp(self):
        # 1. Create a verified Lender
        self.lender = User.objects.create_user(username="lender", email="lender@rentbase.hu", password="Password123!")
        self.lender.userprofile.verification_status = 'verified'
        self.lender.userprofile.save()

        # 2. Create a verified Renter
        self.renter = User.objects.create_user(username="renter", email="renter@rentbase.hu", password="Password123!")
        self.renter.userprofile.verification_status = 'verified'
        self.renter.userprofile.save()

        # 3. Create an Item
        self.item = Item.objects.create(
            lender=self.lender,
            title="Test Camera",
            category="electronics",
            condition="good",
            daily_price=5000.00,
            estimated_value=200000.00,
            security_deposit=40000.00,
            pickup_location="Budapest"
        )

        # 4. Create a Pending Booking
        self.booking = Booking.objects.create(
            item=self.item,
            renter=self.renter,
            lender=self.lender,
            start_date="2026-04-01",
            end_date="2026-04-03",
            total_days=3,
            rental_fee=15000.00,
            commission_fee=2250.00,
            total_charged=17250.00,
            deposit_amount=40000.00,
            status="pending_payment"
        )

        self.url = reverse('create_payment_intent', kwargs={'booking_id': self.booking.id})

    # We use 'patch' to intercept the call to Stripe so it doesn't leave your computer
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intents_success(self, mock_stripe_create):
        # Create a fake Stripe response
        class FakeIntent:
            def __init__(self, secret):
                self.client_secret = secret

        # Tell our fake Stripe to return two different secrets (one for the rental, one for the deposit)
        mock_stripe_create.side_effect = [
            FakeIntent('pi_rental_123_secret_abc'),
            FakeIntent('pi_deposit_456_secret_def')
        ]

        # Authenticate as the Renter and click "Pay"
        self.client.force_authenticate(user=self.renter)
        response = self.client.post(self.url)

        # Check if we got the 200 OK and both secrets
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("rental_client_secret", response.data)
        self.assertIn("deposit_client_secret", response.data)

        # Check the database to make sure it recorded the transactions
        self.assertTrue(Payment.objects.filter(booking=self.booking).exists())
        self.assertTrue(DepositHold.objects.filter(booking=self.booking).exists())

        # Verify the deposit hold was set up correctly
        hold = DepositHold.objects.get(booking=self.booking)
        self.assertEqual(hold.status, 'held')
        self.assertEqual(hold.amount, 40000.00)