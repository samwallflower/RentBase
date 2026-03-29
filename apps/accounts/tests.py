from django.test import TestCase

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User, UserProfile


class AuthenticationTests(APITestCase):

    def test_user_registration(self):
        """Test that a new user can register successfully"""
        url = reverse('register')
        data = {
            "email": "testuser@rentbase.hu",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "StrongPassword123!"
        }

        # Act like a frontend sending data to the API
        response = self.client.post(url, data)

        # Check that the response is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the user exists in the database
        user_exists = User.objects.filter(email="testuser@rentbase.hu").exists()
        self.assertTrue(user_exists)

        # Check that our Signal automatically created a UserProfile
        user = User.objects.get(email="testuser@rentbase.hu")
        self.assertTrue(hasattr(user, 'userprofile'))
        self.assertEqual(user.userprofile.verification_status, 'unverified')