from django.shortcuts import render
from companion_app import models
from .serializers import ChatsSerializer
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
import logging
import json
import base64
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from cartesia import Cartesia
import groq

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))

# Initialize Cartesia client
cartesia_client = Cartesia(api_key=os.getenv('CARTESIA_API_KEY'))

class HistoryChat(generics.ListCreateAPIView):
    queryset = models.Chat_History.objects.all()
    serializer_class = ChatsSerializer

@api_view(['GET'])
def GetDeepgramAPI(request):
    api_key = os.getenv('DEEPGRAM_API_KEY')
    return Response({'api_key': api_key}, status=HTTP_200_OK)

@api_view(['POST'])
def CreateAccount(request):
    user = User.objects.create_user(request.data['username'], request.data['email'], request.data['password'])
    user.save()
    return Response({'message': 'Account created successfully'}, status=HTTP_201_CREATED)

@api_view(['POST'])
def CheckUser(request):
    user = User.objects.filter(email=request.data['email']).exists()
    if not user:
        CreateAccount(request)
    else:
        return Response({'message': 'User already exists'}, status=HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def ResetChat(request):
    models.Chat_History.objects.filter(user_uid=request.data['user_uid']).delete()
    return Response({'message': 'Chat reset successfully'}, status=HTTP_200_OK)

@api_view(['POST'])
def GetChat(request):
    chat = models.Chat_History.objects.filter(user_uid=request.data['user_uid'])
    serializer = ChatsSerializer(chat, many=True)
    return Response(serializer.data, status=HTTP_200_OK)

@api_view(['PUT'])
def AddChat(request):
    text = request.data['text']
    user_uid = request.data['user_uid']
    isUser = request.data['isUser']

    models.Chat_History.objects.create(text=text, user_uid=user_uid, isUser=isUser)
    
    return Response({'message': 'Chat added successfully'}, status=HTTP_200_OK)