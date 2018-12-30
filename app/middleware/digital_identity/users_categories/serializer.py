from rest_framework import serializers

from . import models

class UserDetailsSerializer(serializers.ModelSerializer):
    """Serializer for user profile objects"""

    class Meta:
        model = models.UserDetail
        fields = (
            'id', 'user_id', 'user_name', 'email', 'gender',
        )

    def create(self, validated_data):
        """Create and return a new user"""

        user = models.UserDetail(
            user_id = validated_data['user_id'],
            user_name=validated_data['user_name'],
            email = validated_data['email'],
            gender=validated_data['gender'],
        )
        user.save()
        return user

