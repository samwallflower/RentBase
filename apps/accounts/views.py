from django.shortcuts import render

from rest_framework import generics, permissions
from .models import User
from .serializers import RegisterSerializer, UserSerializer

class RegisterView(generics.CreateAPIView):
    # Anyone can access this (you don't need to be logged in to register)
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    # You MUST be logged in (authenticated) to view or edit your profile
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        # This automatically fetches the user making the request
        return self.request.user