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
    
class CustomUserViewSet(viewsets.ViewSet):
    lookup_field = 'username'
    def get_permissions(self):
        if self.action == 'partial_update' or self.action == 'update' or self.action == 'destroy':
            return [IsSameUserOrReadOnly()]
        return [AllowAny()]
    
    def list(self,request):
        queryset = CustomUser.objects.all()
        serializer = CustomUserSerializer(queryset,many=True)
        return Response(serializer.data)
    
    def retrieve(self,request,username=None):
        try:
            queryset = CustomUser.objects.all()
            user = get_object_or_404(queryset,username=username)
            serializer = self.get_serializer(user)
        except ValueError:
            return Response({'ValueError':"Please enter the correct username for field 'username'"})
        except AssertionError:
            return Response({'Server Error':'Something has been broken on our side, please come after some time'})
        return Response(serializer.data)
    
    def create(self,request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except AssertionError:
            return Response({'Server Error':'Something has been broken on our side, please come after some time'},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        return Response(serializer.data)

    def partial_update(self,request,pk):
        user = get_object_or_404(CustomUser,pk=pk)
        serializer = CustomUserSerializer(instance=user,data = request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_206_PARTIAL_CONTENT)

    def destroy(self,request,pk):
        user = get_object_or_404(CustomUser,pk=pk)
        self.check_object_permissions(request,user)
        user.delete()

        return Response({'Detail':'Account Deleted Successfully'},status=status.HTTP_204_NO_CONTENT)
    
    def get_serializer(self,*args,**kwargs):
        return CustomUserSerializer(*args,context=self.get_serializer_context(),**kwargs)
    
    def get_serializer_context(self):
        return {'request':self.request}
    
class PostViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action == 'partial_update' or  self.action == 'update' or self.action == 'destroy':
            return [IsAuthorOrReadOnly()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = Post.objects.all().select_related('author')
        return queryset
    
    def list(self,request):
        queryset = self.get_queryset()
        serializer = PostSerializer(queryset,many=True)
        return Response(serializer.data)
    
    def retrieve(self,request,pk=None):
        queryset = self.get_queryset()
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

    def destroy(self,request,pk):
        instance = get_object_or_404(Post,pk=pk)
        instance.delete()

        return Response({'Detail':'Deleted Successfully'},status=status.HTTP_204_NO_CONTENT)

    def get_serializer(self,*args,**kwargs):
        return PostSerializer(*args,context=self.get_serializer_context(),**kwargs)
    
    def get_serializer_context(self,*args,**kwargs):
        return {'request':self.request}


# Create your views here.
