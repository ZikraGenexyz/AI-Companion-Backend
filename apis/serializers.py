from rest_framework import serializers
from companion_app import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user_uid',
            'text',
            'isUser'
        )
        model = models.Chat_History

# class CreateAccountSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = (
#             'username',
#             'email',
#             'password'
#         )
#         model = User

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         user.save()
#         return user

class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceToken
        fields = ['id', 'user_id', 'device_token', 'device_type', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']