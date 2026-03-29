from rest_framework import serializers
from .models import User, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        # We only expose safe fields. Notice we don't expose the user ID here.
        fields = ['avatar', 'bio', 'location', 'verification_status',
                  'average_rating_lender', 'average_rating_renter']
        read_only_fields = ['verification_status', 'average_rating_lender', 'average_rating_renter']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        # We must use create_user so the password gets hashed (encrypted)!
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile']