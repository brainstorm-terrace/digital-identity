from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import UserDetailsSerializer
from rest_framework.response import Response
from rest_framework import status
from . import models

# Create your views here.
class UserDetailsView(APIView):
    """
        User details
    """
    def post(self, request):
        data = request.data
        serializer = UserDetailsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
