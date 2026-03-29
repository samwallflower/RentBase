from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.bookings.models import Booking
from apps.payments.models import Payment, DepositHold
from apps.verification.permissions import IsVerified
from .stripe_service import create_rental_intent, create_deposit_hold

class CreatePaymentIntentView(APIView):
    # Only verified users can pay for things!
    permission_classes = [IsVerified]

    def post(self, request, booking_id):
        # 1. Find the booking the user is trying to pay for
        booking = get_object_or_404(Booking, id=booking_id)

        # 2. Security Check: Ensure the person paying is actually the renter
        if booking.renter != request.user:
            return Response(
                {"error": "You cannot pay for someone else's booking."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 3. Security Check: Make sure it hasn't already been paid for
        if booking.status != 'pending_payment':
            return Response(
                {"error": "This booking is no longer pending payment."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 4. Ask Stripe to generate the two financial transactions
            rental_secret = create_rental_intent(booking)
            deposit_secret = create_deposit_hold(booking)

            # 5. Save the Stripe IDs to our database so we can track them later
            Payment.objects.update_or_create(
                booking=booking,
                defaults={
                    'stripe_payment_intent_id': rental_secret.split('_secret')[0],
                    'amount_charged': booking.total_charged,
                    'status': 'pending'
                }
            )

            DepositHold.objects.update_or_create(
                booking=booking,
                defaults={
                    'stripe_payment_intent_id': deposit_secret.split('_secret')[0],
                    'amount': booking.deposit_amount,
                    'status': 'held'
                }
            )

            # 6. Send the secrets back to the frontend to render the credit card forms
            return Response({
                "rental_client_secret": rental_secret,
                "deposit_client_secret": deposit_secret
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)