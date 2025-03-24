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
from serpapi import GoogleSearch

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))

# Initialize Cartesia client
cartesia_client = Cartesia(api_key=os.getenv('CARTESIA_API_KEY'))

class HistoryChat(generics.ListCreateAPIView):
    queryset = models.Chat_History.objects.all()
    serializer_class = ChatsSerializer

@api_view(['POST'])
def ResetChat(request):
    models.Chat_History.objects.filter(user_uid=request.data['user_uid']).delete()
    return Response({'message': 'Chat reset successfully'}, status=HTTP_200_OK)

@api_view(['POST'])
def GetChat(request):
    chat = models.Chat_History.objects.filter(user_uid=request.data['user_uid'], isUser=True)
    summary = ''
    for c in chat:
        summary += c.text + ', '
    summary = summary.rstrip(', ')

    # summary += '[Dont Reply to this message]'

    return Response({'summary': summary}, status=HTTP_200_OK)

@api_view(['PUT'])
def AddChat(request):
    text = request.data['text']
    user_uid = request.data['user_uid']
    isUser = True if request.data['isUser'] == 'true' else False

    chat_history = models.Chat_History.objects.filter(user_uid=user_uid).last()

    if chat_history is not None:
        if chat_history.isUser == isUser:
            chat_history.text = text
            chat_history.save()
        else:
            models.Chat_History.objects.create(text=text, user_uid=user_uid, isUser=isUser)
    else:
        models.Chat_History.objects.create(text=text, user_uid=user_uid, isUser=isUser)
    
    return Response({'message': 'Chat added successfully'}, status=HTTP_200_OK)

@api_view(['POST'])
def GoogleSearchApi(request):
    search = GoogleSearch({
        "q": request.data['query'], 
        "location": "Indonesia, Jakarta",
        "api_key": os.getenv('GOOGLE_API_KEY')
    })

    result = search.get_dict()
    result = result['search_results']['related_questions'][0]['snippet']

    return Response({'search_results': result}, status=HTTP_200_OK)