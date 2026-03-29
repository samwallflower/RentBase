import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    # Override username to be optional, email is primary
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email


class UserProfile(TimeStampedModel):
    VERIFICATION_CHOICES = [
        ('unverified', 'Unverified'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # ImageField uses Pillow and saves to our local MEDIA_ROOT
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)

    average_rating_lender = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    average_rating_renter = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_rentals_given = models.PositiveIntegerField(default=0)
    total_rentals_received = models.PositiveIntegerField(default=0)

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default='unverified'
    )

    def __str__(self):
        return f"Profile: {self.user.email}"