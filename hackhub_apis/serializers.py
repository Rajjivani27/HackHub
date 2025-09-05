from rest_framework import serializers
from .models import *
from django.db import transaction

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['name','user_bio','profile_pic','dob','university','github']

class CustomUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer() #Profile Serializer
    password2 = serializers.CharField(write_only=True,style={'input_type':'password'})
    class Meta:
        model = CustomUser
        fields = ['email','username','password','password2','profile']
        extra_kwargs = {
            'password' : {'write_only':True,'style':{'input_type':'password'}}
        }

    def validate(self,data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords are not matching")
        return data

    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()

        Profile.objects.create(user=user,**profile_data)
        return user
    
class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['files']

class PostSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField(read_only=True)
    author = serializers.StringRelatedField(read_only = True)
    author_username = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    media = PostMediaSerializer(many=True,write_only=True)
    github = serializers.CharField(write_only=True,required=False)

    class Meta:
        model = Post
        fields = ['id','title','content','media','github','author','technologies','category','profile_pic','created_at','likes_count','author_username']

    def get_author_username(self,obj):
        request = self.context.get('request')
        author = obj.author
        return author.username

    def get_likes_count(self,obj):
        return obj.likes.count()

    def get_profile_pic(self,obj):
        request = self.context.get('request')
        author = obj.author
        if author.profile.profile_pic:
            return request.build_absolute_uri(author.profile.profile_pic.url)
        
    @transaction.atomic
    def create(self, validated_data):
        github = validated_data.pop('github')
        media = validated_data.pop('media')
        content = validated_data['content']

        print(media)

        add = f"\nGithub Link : {github}"

        content = content + add
        validated_data['content'] = content
        post = Post.objects.create(**validated_data)

        media_objs = [PostMedia(post=post,files=item['files']) for item in media]
        print(f"Media : {media_objs}")
        PostMedia.objects.bulk_create(media_objs)
        return post
    
    def update(self, instance, validated_data):
        if validated_data['media']:
            media = validated_data.pop('media')
            print(f"Media : {media}")
            for item in media:
                print(item['files'])
            media_objs = [PostMedia(post=instance,files=item['files']) for item in media]
            print(f"Media : {media_objs}")
            post = PostMedia.objects.bulk_create(media_objs)
            print(f"Medias : {post}")

        return instance
    
class TeamOpportunitySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = TeamFinder
        fields = ['user','title','details','created_at','last_date']

    def get_created_at(self,obj):
        return obj.created_at

    
class VerifyEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    