from rest_framework import viewsets, filters, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializer
from . import models
from . import permissions
from .serializer import UserProfileSerializer

from dotenv import load_dotenv
from django.conf import settings

import requests
import json
import os

# Create your views here.

class UserProfileViewSet(viewsets.ModelViewSet):
    """Handles creating, updating and deleting profiles"""

    serializer_class = serializer.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name','email',)



class LoginViewSet(viewsets.ViewSet):
    """Checks email and password and returns an auth token"""

    serializer_class = AuthTokenSerializer

    def create(self, request):
        """Use the ObtainAuthToken APIView to validate and create a token"""

        return ObtainAuthToken().post(request)


class UserProfileView(APIView):
    """ User Profile APIView. """

    def post(self, request):
        """ Creates a new user if username and Email didn't exist in the database. """

        user_data = request.data
        user_profile_serializer = UserProfileSerializer(data=user_data)
        if user_profile_serializer.is_valid():
            user_profile_serializer.save()

            '''Create user_id'''
            user_id = self.create_user_id(user_data)

            user_dict = {'user_id':user_id}
            user_dict.update(user_profile_serializer.data)
            return Response(user_dict, status=status.HTTP_201_CREATED)
        return Response(user_profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def create_user_id(self, user_data):
        """ Method to call "users-categories/user-detail" api and return user_id.. """

        user_details_request_data = {
            "user_detail":
                {
                    "user_name": user_data['name'],
                    "email": user_data['email'],
                }
        }

        dotenv_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'config\.env')
        load_dotenv(dotenv_path)
        url = os.getenv('user_id_api_endpoint')
        api_response = requests.post(url, json=user_details_request_data)
        user_details_response = api_response.json()

        return user_details_response['user_id']
