import stripe
from django.conf import settings

# Tell the Stripe library to use your hidden Secret Key
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_rental_intent(booking):
    """Creates a standard payment that charges the Renter immediately."""
    # Note: HUF (Hungarian Forint) is a zero-decimal currency in Stripe.
    # We convert the Decimal to an integer.
    amount = int(booking.total_charged)

    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='huf',
        metadata={
            'booking_id': str(booking.id),
            'type': 'rental_fee'
        }
    )
    return intent.client_secret


def create_deposit_hold(booking):
    """Creates an authorization HOLD on the Renter's card for the deposit."""
    amount = int(booking.deposit_amount)

    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='huf',
        capture_method='manual',  # <-- THIS IS THE MAGIC! It holds the funds without charging.
        metadata={
            'booking_id': str(booking.id),
            'type': 'security_deposit'
        }
    )
    return intent.client_secret