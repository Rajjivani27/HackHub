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
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated,AllowAny
from .permissions import IsAuthorOrReadOnly,IsSameUserOrReadOnly
    
class CustomUserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = CustomUser.objects.all()
    def get_permissions(self):
        if self.action == 'partial_update' or self.action == 'update' or self.action == 'destroy':
            return [IsSameUserOrReadOnly()]
        return [AllowAny()]

    def partial_update(self,request,pk):
        user = get_object_or_404(CustomUser,pk=pk)
        serializer = CustomUserSerializer(instance=user,data = request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_206_PARTIAL_CONTENT)
    
    def get_serializer(self,*args,**kwargs):
        return CustomUserSerializer(*args,context=self.get_serializer_context(),**kwargs)
    
    def get_serializer_context(self):
        return {'request':self.request}
    
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action == 'partial_update' or  self.action == 'update' or self.action == 'destroy':
            return [IsAuthorOrReadOnly()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = Post.objects.all().select_related('author')
        return queryset
    
    def create(self,request):
        data = request.data.copy()

        files = request.FILES.lists()
        files_data = media_processing(files)

        serializer_data = {
            'title': data.get('title'),
            'content': data.get('content'),
            'github': data.get('github'),
            'media': files_data
        }

        serializer = self.get_serializer(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author = request.user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    def partial_update(self,request,pk):
        posts = self.get_queryset()
        post = get_object_or_404(posts,pk=pk)

        self.check_object_permissions(request,post)
        serializer = self.get_serializer(instance=post,data = request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status = status.HTTP_206_PARTIAL_CONTENT)
    
    def update(self,request,pk):
        post = get_object_or_404(Post,pk=pk)
        self.check_object_permissions(request,post)
        serializer = self.get_serializer(instance=post,data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_205_RESET_CONTENT)

    def get_serializer(self,*args,**kwargs):
        return PostSerializer(*args,context=self.get_serializer_context(),**kwargs)
    
    def get_serializer_context(self,*args,**kwargs):
        return {'request':self.request}


# Create your views here.
