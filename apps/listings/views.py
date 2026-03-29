from django.shortcuts import render

from rest_framework import generics, permissions
from .models import Item
from .serializers import ItemSerializer
from apps.verification.permissions import IsVerified
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .serializers import ItemPhotoSerializer
from django.shortcuts import get_object_or_404

class ItemListCreateView(generics.ListCreateAPIView):
    # Only show active listings to the public
    queryset = Item.objects.filter(is_active=True)
    serializer_class = ItemSerializer

    def get_permissions(self):
        # If they are trying to POST (create an item), deploy the Bouncer!
        if self.request.method == 'POST':
            return [IsVerified()]
        # If they are just GETting (viewing items), let anyone in
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # Automatically attach the logged-in user as the 'lender'
        serializer.save(lender=self.request.user)



class ItemPhotoUploadView(generics.CreateAPIView):
    # Only verified users can upload photos
    permission_classes = [IsVerified]
    serializer_class = ItemPhotoSerializer

    # These parsers tell Django to expect a file upload, not just JSON text
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        # 1. Find the item they are trying to attach the photo to
        item_id = self.kwargs.get('pk')
        item = get_object_or_404(Item, id=item_id)

        # 2. Security Check: Make sure the person uploading the photo actually owns the item!
        if item.lender != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only upload photos to your own listings.")

        # 3. If this is the very first photo, automatically make it the "primary" photo
        is_primary = not item.photos.exists()

        # 4. Save the file to the local VPS media folder
        serializer.save(item=item, is_primary=is_primary)