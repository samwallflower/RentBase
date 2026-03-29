import uuid
from django.db import models
from apps.accounts.models import User, TimeStampedModel


class UserVerification(TimeStampedModel):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('requires_action', 'Requires Action'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    # Stripe References (No PII)
    stripe_session_id = models.CharField(max_length=200, null=True, blank=True)
    stripe_report_id = models.CharField(max_length=200, null=True, blank=True)

    # GDPR Consent & Audit
    tos_accepted_at = models.DateTimeField(null=True, blank=True)
    tos_ip_address = models.GenericIPAddressField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=200, null=True, blank=True)

    @property
    def stripe_dashboard_url(self):
        if self.stripe_session_id:
            return f"https://dashboard.stripe.com/identity/verification_sessions/{self.stripe_session_id}"
        return None

    def __str__(self):
        return f"Verification for {self.user.email} - {self.status}"


class VerificationAccessLog(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification = models.ForeignKey(UserVerification, on_delete=models.CASCADE)
    accessed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    booking_ref_id = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return f"Accessed by {self.accessed_by.email} on {self.created_at}"