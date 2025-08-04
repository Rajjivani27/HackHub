from .utils import *
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView,UpdateAPIView,DestroyAPIView
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated,AllowAny

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
    
class CustomUserViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def list(self,request):
        queryset = CustomUser.objects.all()
        serializer = CustomUserSerializer(queryset,many=True)
        return Response(serializer.data)
    
    def retrieve(self,request,pk=None):
        queryset = CustomUser.objects.all()
        user = get_object_or_404(queryset,pk=pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
    
    def create(self,request):
        serializer = self.get_serializer(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def get_serializer(self,*args,**kwargs):
        return CustomUserSerializer(*args,context=self.get_serializer_context(),**kwargs)
    
    def get_serializer_context(self):
        return {'request':self.request}
    
class PostViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def list(self,request):
        queryset = Post.objects.all()
        serializer = PostSerializer(queryset,many=True)
        return Response(serializer.data)
    
    def retrieve(self,request,pk=None):
        queryset = Post.objects.all()
        post = get_object_or_404(queryset,pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def create(self,request):
        data = request.data.copy()

        files = request.FILES.lists()
        files_data = media_processing(files)

        serializer_data = {
            'title': data.get('title'),
            'content': data.get('content'),
            'media': files_data
        }

        serializer = self.get_serializer(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author = request.user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    def get_serializer(self,*args,**kwargs):
        return PostSerializer(*args,context=self.get_serializer_context(),**kwargs)
    
    def get_serializer_context(self,*args,**kwargs):
        return {'request':self.request}


# Create your views here.
