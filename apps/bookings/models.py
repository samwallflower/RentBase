import uuid
from django.db import models
from apps.accounts.models import User
from apps.listings.models import Item


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('payment_failed', 'Payment Failed'),
        ('confirmed', 'Confirmed & Paid'),
        ('active', 'Active (Picked Up)'),
        ('return_pending', 'Return Initiated'),
        ('completed', 'Completed (Returned)'),
        ('disputed', 'Disputed'),
        ('deposit_released', 'Deposit Released'),
        ('no_return', 'No-Return Reported'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    renter = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bookings_as_renter')
    lender = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bookings_as_lender')

    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.PositiveSmallIntegerField()

    # Financial Snapshots
    rental_fee = models.DecimalField(max_digits=10, decimal_places=2)
    commission_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_charged = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_payment')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    pickup_confirmed_at = models.DateTimeField(null=True, blank=True)
    return_confirmed_at = models.DateTimeField(null=True, blank=True)
    deposit_released_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} - {self.item.title} ({self.status})"


class HandoverAgreement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)

    pickup_agreed_datetime = models.DateTimeField(null=True, blank=True)
    pickup_location_text = models.CharField(max_length=500, blank=True)
    return_agreed_datetime = models.DateTimeField(null=True, blank=True)
    return_location_text = models.CharField(max_length=500, blank=True)

    pickup_confirmed_renter = models.BooleanField(default=False)
    pickup_confirmed_lender = models.BooleanField(default=False)
    return_confirmed_renter = models.BooleanField(default=False)
    return_confirmed_lender = models.BooleanField(default=False)

    is_pickup_finalized = models.BooleanField(default=False)
    is_return_finalized = models.BooleanField(default=False)
    proposed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


class BookingStatusLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.CharField(max_length=30)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class NoReturnReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.PROTECT)
    reported_by = models.ForeignKey(User, on_delete=models.PROTECT)
    last_contact_attempt_at = models.DateTimeField()
    description = models.TextField()
    status = models.CharField(max_length=30, default='filed')
    admin_notes = models.TextField(blank=True)
    identity_accessed = models.BooleanField(default=False)
    law_enforcement_ref = models.CharField(max_length=200, blank=True)
    filed_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)