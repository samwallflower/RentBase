from django.contrib import admin
from .models import Item, ItemPhoto, AvailabilityWindow, MeetupAvailability

admin.site.register(Item)
admin.site.register(ItemPhoto)
admin.site.register(AvailabilityWindow)
admin.site.register(MeetupAvailability)