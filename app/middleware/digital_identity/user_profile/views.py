from rest_framework import viewsets, filters, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core import serializers
from django.http import HttpResponse, JsonResponse

from . import serializer
from . import models
from . import permissions
from .serializer import UserProfileSerializer

from dotenv import load_dotenv
from django.conf import settings
from django.db.models import Q
import requests
import json
import os

# Create your views here.

class UserProfileView(APIView):
    """ User Profile APIView. """

    def get(self, request):
        """ Get list of all users or specified users in the database"""
        request_data = dict(request.GET)

        if request_data:
            """Get list of request users"""
            # print("Request data has some params")
            # print("request_data",request_data)
            name_list = request_data.get('name')
            email_list = request_data.get('email')
            users_qs = models.UserProfile.objects.filter(Q(name__in=name_list) | Q(email__in=email_list)).values('email', 'name', 'is_active', 'is_superuser', 'is_staff')
        else:
            """Get list of all users"""
            # print("Requested data is empty")
            users_qs = models.UserProfile.objects.values('email', 'name', 'is_active', 'is_superuser', 'is_staff')

        return JsonResponse(list(users_qs), safe=False)

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

    def put(self, request,pk):
        """Update name , email and password of a particular user."""
        user_instance = models.UserProfile.objects.get(pk=pk)
        requested_data = request.data
        user_profile_serializer = UserProfileSerializer(user_instance, data=requested_data, partial=True)
        if user_profile_serializer.is_valid():
            user_profile_serializer.save()
            return Response(user_profile_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse("Please provide valid details", safe=False)

    def delete(self, request,pk=None):
        """Delete existing user from the database"""
        request_data = dict(request.GET)
        name = request_data.get('name')
        if name is not None :
            name = name[0]
            try:
                user_instance = models.UserProfile.objects.get(name=name)
                user_instance.delete()
                return Response("User {} is deleted".format(user_instance))
            except Exception as e:
                return Response("User doesn't exist. Please provide a valid user.")
        else:
            try:
                user_instance = models.UserProfile.objects.get(pk=pk)
                user_instance.delete()
                return Response("User {} is deleted".format(user_instance))
            except Exception as e:
                return Response("User doesn't exist. Please provide a valid user.")

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
