from rest_framework import serializers

from . import models

import requests, json


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile objects"""

    class Meta:
        model = models.UserProfile
        fields = ['id', 'email', 'name', 'password',]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Create and return a new user"""

        user = models.UserProfile(
            email = validated_data['email'],
            name = validated_data['name']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update existing user"""
        print("serializer", validated_data)
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)

        instance.set_password = validated_data.get('password', instance.password)
        instance.save()

        return instance
