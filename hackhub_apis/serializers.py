from rest_framework import serializers
from .models import CustomUser,Profile
from django.db import transaction

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['name','user_bio','profile_pic','dob']

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
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        Profile.objects.create(user=user,**profile_data)
        return user
    