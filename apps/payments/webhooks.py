import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from apps.bookings.services import confirm_booking_after_payment


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        # This mathematically proves the message actually came from Stripe and not a hacker
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the successful payment event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']

        # We only want to confirm the booking if this is the RENTAL fee charging.
        # We don't want to trigger this when the Security Deposit simply authorizes.

    # Handle the successful payment event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']

        # Safely check for metadata without using .get()
        if 'metadata' in payment_intent and 'type' in payment_intent['metadata']:
            if payment_intent['metadata']['type'] == 'rental_fee':
                # Only confirm the booking if this is the actual rental charge
                confirm_booking_after_payment(payment_intent['id'])

    return HttpResponse(status=200)