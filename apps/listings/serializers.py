from decimal import Decimal
from rest_framework import serializers
from .models import Item, ItemPhoto

class ItemPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPhoto
        fields = ['id', 'image', 'is_primary', 'order']


class ItemSerializer(serializers.ModelSerializer):
    # This automatically fetches the photos attached to the item
    photos = ItemPhotoSerializer(many=True, read_only=True)
    lender_email = serializers.ReadOnlyField(source='lender.email')

    class Meta:
        model = Item
        fields = [
            'id', 'lender', 'lender_email', 'title', 'description', 'category',
            'daily_price', 'security_deposit', 'estimated_value',
            'condition', 'is_active', 'pickup_location', 'photos'
        ]
        # The user shouldn't send 'lender' in the form, we will set it automatically behind the scenes
        read_only_fields = ['lender']

    def validate(self, data):
        # Enforce your business rule: Deposit >= 20% of Estimated Value
        security_deposit = data.get('security_deposit')
        estimated_value = data.get('estimated_value')

        if security_deposit and estimated_value:
            minimum_deposit = estimated_value * Decimal(0.20)  # 20%
            if float(security_deposit) < float(minimum_deposit):
                raise serializers.ValidationError({
                    "security_deposit": f"Security deposit must be at least 20% of estimated value ({minimum_deposit} HUF)."
                })
        return data