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
import sqlite3
import digital_identity.settings as settings
import pandas as pd
from django.db import connection

# Create your views here.

class UserProfileView(APIView):
    """ User Profile APIView. """

    def get(self, request):
        """ Get list of all users or specified users in the database"""
        request_data = dict(request.GET)
        args_filter_values = ['email', 'name', 'is_active', 'is_superuser', 'is_staff']
        if request_data:
            """Get list of request users"""
            kwargs_name = {key+'__in':value for key,value in request_data.items() if key=='name'}
            kwargs_email = {key + '__in': value for key, value in request_data.items() if key == 'email'}
            users_qs = models.UserProfile.objects.filter(Q(**kwargs_name)|Q(**kwargs_email)).values(*args_filter_values)
        else:
            """Get list of all users"""
            users_qs = models.UserProfile.objects.values(*args_filter_values)
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

    def put(self, request):
        """Update name , email and password of a particular user."""
        db_path = os.path.join(settings.BASE_DIR, settings.DATABASES['default']['NAME'])
        # print("db_path", db_path)
        conn = sqlite3.connect(db_path)
        # print(conn)

        # users = dict(request.GET)
        # print("users", users)

        user_data = request.data
        # print("user_data", user_data)
        user_data_dict = {user['name']:user for user in user_data}
        # print("user_data_dict", user_data_dict)

        sql_query = "SELECT * FROM user_profile_userprofile WHERE name in {}".format(tuple(user_data_dict.keys()))
        # print("sql_query", sql_query)
        pd_users = pd.read_sql(sql_query, conn)
        # print(pd_users)
        # pd_users.to_csv('csv_file.csv')

        pd_user_data = pd.DataFrame(data=user_data, columns=list(pd_users.columns.values))
        left_name = pd_users.set_index('name')
        right_name = pd_user_data.set_index('name')

        res = left_name.reindex(columns=left_name.columns.union(right_name.columns))
        res.update(right_name)
        res.reset_index(inplace=True)
        print(res)

        # res.to_sql(name='my_temp', con = conn, if_exists='append', index=False )

        conn.execute('DELETE from user_profile_userprofile WHERE name in {}'.format(tuple(user_data_dict.keys())))
        res.to_sql(name='user_profile_userprofile', con=conn, if_exists='append', index=False)

        conn.close()
        return JsonResponse("Update Successful", safe=False)

    def delete(self, request):
        """Delete existing user from the database - set is_active flag to false"""
        request_data = dict(request.GET)
        # name = request_data.get('name')
        # email = request_data.get('email')

        if request_data:
            kwargs_name = {key + '__in': value for key, value in request_data.items() if key == 'name'}
            kwargs_email = {key + '__in': value for key, value in request_data.items() if key == 'email'}
            models.UserProfile.objects.filter(Q(**kwargs_name) | Q(**kwargs_email)).update(is_active=False)
            print("Updated is_active status")
            return JsonResponse("Deleted the user", safe=False)
        else:
            return JsonResponse("Plese select a user to be deleted", self=False)

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
