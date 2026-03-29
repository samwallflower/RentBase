import stripe
from django.conf import settings
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_verification_session(user, ip_address=None):
    """
    Records ToS acceptance and creates a Stripe Identity session.
    If STRIPE_SECRET_KEY is empty, bypasses Stripe and auto-verifies (Dev Mode).
    """
    verification_record = user.userverification
    verification_record.tos_accepted_at = timezone.now()
    verification_record.tos_ip_address = ip_address

    # DEV MODE BYPASS
    if not settings.STRIPE_SECRET_KEY:
        verification_record.status = 'verified'
        verification_record.verified_at = timezone.now()
        verification_record.save()

        user.userprofile.verification_status = 'verified'
        user.userprofile.save()
        return "dev_mode_auto_verified"

    # REAL STRIPE MODE
    session = stripe.identity.VerificationSession.create(
        type='document',
        metadata={'user_id': str(user.id), 'email': user.email},
        options={
            'document': {
                'allowed_types': ['id_card', 'passport', 'driving_license'],
                'require_id_number': True,
                'require_matching_selfie': True,
            }
        }
    )

    verification_record.stripe_session_id = session.id
    verification_record.status = 'pending'
    verification_record.submitted_at = timezone.now()
    verification_record.save()

    user.userprofile.verification_status = 'pending'
    user.userprofile.save()

    return session.client_secret