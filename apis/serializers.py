from rest_framework import serializers
from companion_app import models
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'username',
            'email',
            'password'
        )
        model = models.User_Data

class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'key',
            'chat'
        )
        model = models.Chat_History

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'email',
            'password'
        )
        model = User