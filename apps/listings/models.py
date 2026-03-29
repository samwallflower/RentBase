import uuid
from django.db import models
from apps.accounts.models import User, TimeStampedModel


class Item(TimeStampedModel):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('tools', 'Tools'),
        ('sports', 'Sports'),
        ('outdoor', 'Outdoor'),
        ('musical', 'Musical Instruments'),
        ('photography', 'Photography'),
        ('other', 'Other'),
    ]
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    # Financials (in HUF)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2)

    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    is_active = models.BooleanField(default=True)  # Lenders can pause their listings
    pickup_location = models.CharField(max_length=300)  # General area only

    @property
    def is_available(self):
        # We will add advanced availability logic later, but this acts as a quick check
        return self.is_active

    def __str__(self):
        return f"{self.title} (Lender: {self.lender.email})"


class ItemPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='photos')

    image = models.ImageField(upload_to='listings/')
    is_primary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Photo for {self.item.title}"


class AvailabilityWindow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='availability_windows')
    start_date = models.DateField()
    end_date = models.DateField()

    # True = Item is NOT available (rented out or under maintenance)
    is_blocked = models.BooleanField(default=False)
    note = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.item.title}: {self.start_date} to {self.end_date} (Blocked: {self.is_blocked})"


class MeetupAvailability(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='meetup_slots')
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.item.title}: {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"