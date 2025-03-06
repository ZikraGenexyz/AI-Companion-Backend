from rest_framework import serializers
from companion_app import models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'username'
        )
        model = models.User_Data

class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'key',
            'chat'
        )
        model = models.Chat_History