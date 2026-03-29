import uuid
from django.db import models
from apps.bookings.models import Booking


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)

    # This will hold "fake_intent_123" when Dev Mode is active
    stripe_payment_intent_id = models.CharField(max_length=200, unique=True, null=True, blank=True)
    amount_charged = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='huf')
    status = models.CharField(max_length=30, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.id} ({self.status})"


class DepositHold(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)

    stripe_payment_intent_id = models.CharField(max_length=200, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # held = Authorized on card. released = Cancelled hold. captured = Taken for dispute.
    status = models.CharField(max_length=20, default='pending')

    authorized_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    captured_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Deposit for Booking {self.booking.id} ({self.status})"