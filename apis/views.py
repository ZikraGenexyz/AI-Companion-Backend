from django.shortcuts import render
from companion_app import models
from .serializers import UserSerializer, ChatsSerializer
from rest_framework import generics

# Create your views here.
class ListUser(generics.ListCreateAPIView):
    queryset = models.User_Data.objects.all()
    serializer_class = UserSerializer

class HistoryChat(generics.ListCreateAPIView):
    queryset = models.Chat_History.objects.all()
    serializer_class = ChatsSerializer
