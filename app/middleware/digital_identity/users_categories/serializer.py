from rest_framework import serializers

from . import models

class UserDetailsSerializer(serializers.ModelSerializer):
    """Serializer for user profile objects"""

    class Meta:
        user_id = "Madhu"
        model = models.UserDetail
        fields = (
            'id', 'user_id', 'email', 'user_name',
        )


    def create(self, validated_data):
        """Create and return a new user"""
        print("validated_data", validated_data)
        user = models.UserDetail(
            user_id = validated_data['user_id'],
            user_name=validated_data['user_name'],
            email = validated_data['email'],
        )
        user.save()
        return user


