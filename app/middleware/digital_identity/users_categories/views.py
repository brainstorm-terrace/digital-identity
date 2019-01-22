from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import UserDetailsSerializer
from rest_framework.response import Response
from rest_framework import status

from django.http import JsonResponse
from django.db.models import Q
from . import models
import hashlib
import os
import sqlite3
from digital_identity import settings
import pandas as pd


# Create your views here.
class UserDetailsView(APIView):
    """
        User details
    """
    def post(self, request):
        """ Creatas a new user and generates hashKey"""
        user_data = request.data['user_detail']
        user_id_hashKey = hashlib.md5(user_data['user_name'].rstrip().encode('utf-8')).hexdigest()
        user_data['user_id'] = user_id_hashKey

        serializer = UserDetailsSerializer(data=user_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):
        """Get list of all users or specified users from database"""
        request_data = dict(request.GET)

        if request_data:
            """Get details of specific user"""
            name_list = request_data.get('user_name')
            # email_list = request_data.get('email')
            # user_id_list = request_data.get('user_id')
            user_name_lookup = Q(user_name__in=name_list)

            # email_lookup = Q(email__in=email_list)
            # user_id_lookup = Q(user_id__in=user_id_list)

            user_qs = models.UserDetail.objects.filter(user_name_lookup).values(
                    'user_id', 'user_name', 'email', 'first_name', 'last_name', 'dob', 'is_active', 'created_on',
                    'updated_at', 'gender', 'linked_in_profile', 'facebook_profile')

            # user_qs = models.UserDetail.objects.filter( user_name_lookup | email_lookup | user_id_lookup).values('user_id','user_name','email','first_name','last_name', 'dob','is_active','created_on','updated_at','gender','linked_in_profile','facebook_profile')

        else:
            """Get all users"""
            user_qs = models.UserDetail.objects.values('user_id','user_name','email','first_name','last_name', 'dob','is_active','created_on','updated_at','gender','linked_in_profile','facebook_profile')

        return JsonResponse(list(user_qs), safe=False)

    def put(self, request):
        """Update details of a particular user."""
        db_path = os.path.join(settings.BASE_DIR, settings.DATABASES['default']['NAME'])
        conn = sqlite3.connect(db_path)
        user_data = request.data
        print(user_data)
        user_data_dict = {user['user_name']:user for user in user_data}

        print(user_data_dict)

        if len(user_data_dict.keys())>1:
            user_data_dict_keys = tuple(user_data_dict.keys())
            sql_query = "SELECT * FROM users_categories_userdetail WHERE user_name in {}".format(user_data_dict_keys)
            delete_query = "DELETE from users_categories_userdetail WHERE user_name in {}".format(user_data_dict_keys)
        else:
            user_data_dict_keys = tuple(user_data_dict.keys())[0]
            sql_query = "SELECT * FROM users_categories_userdetail WHERE user_name in ('{}')".format(user_data_dict_keys)
            delete_query = "DELETE from users_categories_userdetail WHERE user_name in ('{}')".format(user_data_dict_keys)

        print(user_data_dict_keys)

        # sql_query = "SELECT * FROM users_categories_userdetail WHERE user_name in {}".format(user_data_dict_keys)
        print(sql_query)
        pd_users = pd.read_sql(sql_query, conn)

        pd_user_data = pd.DataFrame(data=user_data, columns=list(pd_users.columns.values))
        left_name = pd_users.set_index('user_name')
        right_name = pd_user_data.set_index('user_name')

        res = left_name.reindex(columns=left_name.columns.union(right_name.columns))
        res.update(right_name)
        res.reset_index(inplace=True)

        # conn.execute('DELETE from users_categories_userdetail WHERE user_name in {}'.format(user_data_dict_keys))
        conn.execute(delete_query)
        res.to_sql(name='users_categories_userdetail', con=conn, if_exists='append', index=False)

        conn.close()
        return JsonResponse("Update Successful", safe=False)


    def delete(self, request):
        """Delete existing user from the database - set is_active flag to false"""
        request_data = dict(request.GET)

        if request_data:
            user_name = {key + '__in': value for key, value in request_data.items() if key == 'user_name'}
            kwargs_email = {key + '__in': value for key, value in request_data.items() if key == 'email'}
            models.UserDetail.objects.filter(Q(**user_name) | Q(**kwargs_email)).update(is_active=False)
            print("Updated is_active status")
            return JsonResponse("Deleted the user", safe=False)
        else:
            return JsonResponse("Plese select a user to be deleted", self=False)