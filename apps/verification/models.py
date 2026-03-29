import uuid
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField
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
    # Links this verification record directly to a specific user
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    # We will get this from Stripe later
    stripe_session_id = models.CharField(max_length=200, null=True, blank=True)

    # --- SECURE ENCRYPTED FIELDS ---
    legal_first_name = EncryptedCharField(max_length=200, null=True, blank=True)
    legal_last_name = EncryptedCharField(max_length=200, null=True, blank=True)
    id_document_number = EncryptedCharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Verification for {self.user.email} - {self.status}"
