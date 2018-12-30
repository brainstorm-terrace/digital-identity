from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import UserDetailsSerializer
from rest_framework.response import Response
from rest_framework import status
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
