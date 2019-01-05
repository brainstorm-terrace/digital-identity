from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import UserDetailsSerializer
from rest_framework.response import Response
from rest_framework import status

from django.http import JsonResponse
from django.db.models import Q
from . import models
import hashlib

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

    def delete(self, request,pk=None):
        """Delete existing user from the database"""
        request_data = dict(request.GET)
        user_name = request_data.get('user_name')
        print(user_name)
        if user_name is not None:
            user_name = user_name[0]
            print(user_name)
            try:
                user_instance = models.UserDetail.objects.get(user_name=user_name)
                user_instance.delete()
                return Response("User {} is deleted".format(user_instance))
            except Exception as e:
                return Response("User doesn't exist. Please provide a valid user.")
        else:
            try:
                user_instance = models.UserDetail.objects.get(pk=pk)
                user_instance.delete()
                return Response("User {} is deleted".format(user_instance))
            except Exception as e:
                return Response("User doesn't exist. Please provide a valid user.")
