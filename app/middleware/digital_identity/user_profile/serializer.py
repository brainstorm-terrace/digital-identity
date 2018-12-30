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

        #Create user detail and fetch user_id

        # user_details_request_data = {
        #     "user_detail":
        #         {
        #             "user_name" : validated_data['name'],
        #             "email" : validated_data['email'],
        #         }
        # }
        # # user_details_request_data = json.dumps(user_details_request_data)
        #
        # api_response = requests.post('http://127.0.0.1:8000/users-categories/user-detail', json = user_details_request_data)
        #
        # user_details_response = api_response.json()
        # user_id = user_details_response['user_id']
        #
        # print("user_id", user_id)

        user.set_password(validated_data['password'])
        user.save()

        return user