import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.accounts.models import User
from .models import Item



class ListingTests(APITestCase):
    def setUp(self):
        # 1. Create an UNVERIFIED user
        self.unverified_user = User.objects.create_user(
            username="unverified",
            email="unverified@rentbase.hu",
            password="Password123!"
        )

        # 2. Create a VERIFIED user
        self.verified_user = User.objects.create_user(
            username="verified",
            email="verified@rentbase.hu",
            password="Password123!"
        )
        # Manually verify them for the test
        self.verified_user.userprofile.verification_status = 'verified'
        self.verified_user.userprofile.save()

        self.url = reverse('item_list_create')

        # Standard valid item data (Deposit is exactly 20% of 500,000)
        self.valid_item_data = {
            "title": "Sony A7III Camera",
            "description": "Great mirrorless camera for weekend shoots.",
            "category": "photography",
            "condition": "like_new",
            "daily_price": 5000.00,
            "estimated_value": 500000.00,
            "security_deposit": 100000.00,
            "pickup_location": "Deák Ferenc tér"
        }

    def test_unverified_user_cannot_create_listing(self):
        """Ensure the Bouncer blocks unverified users from posting items"""
        self.client.force_authenticate(user=self.unverified_user)
        response = self.client.post(self.url, self.valid_item_data)

        # Should return 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Item.objects.count(), 0)

    def test_verified_user_can_create_listing(self):
        """Ensure verified users can successfully post items"""
        self.client.force_authenticate(user=self.verified_user)
        response = self.client.post(self.url, self.valid_item_data)

        # Should return 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Item.objects.count(), 1)

        # Check that the system automatically assigned the logged-in user as the lender
        item = Item.objects.first()
        self.assertEqual(item.lender, self.verified_user)

    def test_security_deposit_business_rule(self):
        """Ensure the API rejects deposits that are less than 20% of the estimated value"""
        self.client.force_authenticate(user=self.verified_user)

        invalid_data = self.valid_item_data.copy()
        invalid_data['security_deposit'] = 50000.00  # Only 10% of 500,000!

        response = self.client.post(self.url, invalid_data)

        # Should return 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('security_deposit', response.data)
        self.assertEqual(Item.objects.count(), 0)


class ItemPhotoUploadTests(APITestCase):
    def setUp(self):
        # 1. Create the real owner (Lender)
        self.lender = User.objects.create_user(
            username="lender", email="lender@rentbase.hu", password="Password123!"
        )
        self.lender.userprofile.verification_status = 'verified'
        self.lender.userprofile.save()

        # 2. Create another user (to test security)
        self.other_user = User.objects.create_user(
            username="hacker", email="hacker@rentbase.hu", password="Password123!"
        )
        self.other_user.userprofile.verification_status = 'verified'
        self.other_user.userprofile.save()

        # 3. Create an Item owned by the Lender
        self.item = Item.objects.create(
            lender=self.lender,
            title="DJI Drone",
            description="4K Camera Drone",
            category="electronics",
            condition="like_new",
            daily_price=8000.00,
            estimated_value=300000.00,
            security_deposit=60000.00,
            pickup_location="Budapest"
        )
        self.url = reverse('item_photo_upload', kwargs={'pk': self.item.id})

    def generate_dummy_photo(self):
        """Creates a fake 100x100 pixel image in memory for testing"""
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color=(255, 0, 0))
        image.save(file, 'jpeg')
        file.name = 'test_image.jpg'
        file.seek(0)
        return SimpleUploadedFile(file.name, file.read(), content_type='image/jpeg')

    def test_lender_can_upload_photo(self):
        """Ensure the owner of the item can upload a photo"""
        self.client.force_authenticate(user=self.lender)
        photo_file = self.generate_dummy_photo()

        # Notice we use format='multipart' to tell Django this is a file upload!
        response = self.client.post(self.url, {'image': photo_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.item.photos.count(), 1)

        # Check that the very first photo automatically became the primary one
        self.assertTrue(self.item.photos.first().is_primary)

    def test_non_owner_cannot_upload_photo(self):
        """Ensure users cannot upload photos to an item they do not own"""
        self.client.force_authenticate(user=self.other_user)
        photo_file = self.generate_dummy_photo()

        response = self.client.post(self.url, {'image': photo_file}, format='multipart')

        # Should be blocked by our custom PermissionDenied check (403 Forbidden)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ensure no photo was actually saved to the database
        self.assertEqual(self.item.photos.count(), 0)