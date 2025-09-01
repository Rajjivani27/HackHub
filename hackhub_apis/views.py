from .utils import *
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView,UpdateAPIView,DestroyAPIView,GenericAPIView
from rest_framework import status
from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated,AllowAny
from .permissions import IsAuthorOrReadOnly,IsSameUserOrReadOnly
from django.dispatch import receiver
from django.db.models.signals import (
    post_save,
    post_delete
)
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
import google.generativeai as genai
from HackHub import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

chat_session = model.start_chat(history=[])

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
    def get_queryset(self):
        return Post.objects.all()
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action == 'partial_update' or  self.action == 'update' or self.action == 'destroy':
            return [IsAuthorOrReadOnly()]
        return [AllowAny()]
    
    
    def list(self, request, *args, **kwargs):
        """
        Use self.get_queryset() method to get queryset instead of using-
        self.queryset variable for cache purpose.
        Because in get_queryset() method, queryset everytime get evaluated,
        whereas in variable its get evaluated only one time.
        """
        cache_key = "posts_lists"
        posts = cache.get(cache_key)

        if posts is None:
            serializer = self.get_serializer(self.get_queryset(),many=True)
            posts = serializer.data
            cache.set(cache_key,posts,timeout=60 * 15)

        return Response(posts,status=status.HTTP_200_OK)
    
    def get_queryset(self):
        queryset = Post.objects.all().select_related('author')
        return queryset
    
    def create(self,request):
        data = request.data.copy()

        title = data.get('title')
        content = data.get('content')

        abusive_words = abuse_detector(title,content,chat_session)

        if abusive_words != []:
            response = {'inappropriate content' : 'In your post,we have found some abusive/vulgur words/content or inappropriate langauge, please remove it for doing a post'}
            return Response(response,status=status.HTTP_406_NOT_ACCEPTABLE)

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
    
class EmailVerificationAPI(GenericAPIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = []
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uid']
        token = serializer.validated_data['token']

        try:
            user_id = force_bytes(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id = user_id)
        except(TypeError,ValueError,OverflowError,CustomUser.DoesNotExist):
            user = None
        if user and email_verification_token.check_token(user,token):
            user.is_active = True
            user.save()

            return Response({"Success" : "Email verification successful"},status=status.HTTP_200_OK)
        else:
            return Response({"Error" : "Invalid or expired verification link"},status=status.HTTP_400_BAD_REQUEST)

        


# Create your views here.
