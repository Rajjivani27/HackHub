from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','username','password']
        extra_kwargs = {
            'password' : {'write_only':True,'style':{'input_type':'password'}}
        }