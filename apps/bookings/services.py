from django.utils import timezone
from .models import Booking, BookingStatusLog
from apps.listings.models import AvailabilityWindow
from apps.payments.models import Payment


def confirm_booking_after_payment(payment_intent_id):
    """Handles the business logic after a successful Stripe charge."""
    try:
        # Find the payment by the Stripe ID
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
        booking = payment.booking

        # If it's already confirmed, don't do it again
        if booking.status != 'pending_payment':
            return

        # 1. Update Payment Status
        payment.status = 'succeeded'
        payment.paid_at = timezone.now()
        payment.save()

        # 2. Update Booking Status
        old_status = booking.status
        booking.status = 'confirmed'
        booking.save()

        # 3. Log the status change
        BookingStatusLog.objects.create(
            booking=booking,
            old_status=old_status,
            new_status='confirmed',
            note="Stripe payment succeeded."
        )

        # 4. Block the item's calendar so no one else can rent it!
        AvailabilityWindow.objects.create(
            item=booking.item,
            start_date=booking.start_date,
            end_date=booking.end_date,
            is_blocked=True,
            note=f"Booked - Booking {booking.id}"
        )

        # (In Phases 5 and 6, we will add the ChatRoom and Review logic here!)
        return booking

    except Payment.DoesNotExist:
        pass