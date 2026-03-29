from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import UserVerification

@receiver(post_save, sender=User)
def create_user_verification(sender, instance, created, **kwargs):
    if created:
        UserVerification.objects.create(user=instance)