from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView,UpdateAPIView,DestroyAPIView
from rest_framework import status

class CustomUserCreateAPI(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(request.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def get_serializer_context(self):
        return {'request':self.request}

# Create your views here.
