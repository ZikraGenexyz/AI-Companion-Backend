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
import requests

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
def User_Init(request):
    user_id = request.data['user_id']
    email = request.data['email']
    username = request.data['username']

    if models.Users.objects.filter(user_id=user_id).first() is None:
        models.Users.objects.create(user_id=user_id, email=email, username=username, active=True)

    if models.Friends.objects.filter(user_id=user_id).first() is None:
        models.Friends.objects.create(user_id=user_id, friend_list={}, notification={})
    
    return Response({'message': 'User initialized successfully'}, status=HTTP_200_OK)

@api_view(['DELETE'])
def ResetChat(request):
    models.Chat_History.objects.filter(user_id=request.data['user_id']).delete()
    return Response({'message': 'Chat reset successfully'}, status=HTTP_200_OK)

@api_view(['GET'])
def GetChat(request):
    chat = models.Chat_History.objects.filter(user_id=request.data['user_id'], isUser=True)
    summary = ''
    for c in chat:
        summary += c.text + ', '
    # summary = summary.rstrip(', ')

    summary += '[do not respond]'

    return Response({'summary': summary}, status=HTTP_200_OK)

@api_view(['POST'])
def AddChat(request):
    text = request.data['text']
    user_id = request.data['user_id']
    isUser = True if request.data['isUser'] == 'true' else False

    chat_history = models.Chat_History.objects.filter(user_id=user_id).last()

    if chat_history is not None:
        if chat_history.isUser == isUser:
            chat_history.text = text
            chat_history.save()
        else:
            models.Chat_History.objects.create(text=text, user_id=user_id, isUser=isUser)
    else:
        models.Chat_History.objects.create(text=text, user_id=user_id, isUser=isUser)
    
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

@api_view(['POST'])
def GenerateImage(request):

    engine_id = "stable-diffusion-v1-6"
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    api_key = os.getenv('STABILITY_API_KEY')

    if api_key is None:
        raise Exception("Missing Stability API key.")

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": request.data['prompt']
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 576,
            "samples": 1,
            "steps": 30,
        },
    )

    if response.status_code == 200:
        data = response.json()

        image_data = data['artifacts'][0]['base64']

        # Encode binary image data to base64
        # image_data = base64.b64encode(response.content).decode('utf-8')
        
        return Response({
            'success': True,
            'image': image_data,
            # 'content_type': response.headers.get('Content-Type', 'image/jpeg')
        }, status=HTTP_200_OK)
    else:
        return Response({
            'success': False, 
            'error': response.json()
        }, status=HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def Get_Friend_List(request):
    friend_list = models.Friends.objects.filter(user_id=request.data['user_id']).first().friend_list

    friends = []
    pending = []
    requested = []

    for i, friend_id in enumerate(friend_list['friends']):
        user = models.Users.objects.filter(user_id=friend_id).first()
        friends.append({
            'id': str(i),
            'name': user.user_id,
            'email': user.email,
            'status': 'online'
        })

    for i, friend_id in enumerate(friend_list['pending']):
        user = models.Users.objects.filter(user_id=friend_id).first()
        pending.append({
            'id': str(i),
            'name': user.user_id,
            'email': user.email,
            'status': 'offline'
        })

    for i, friend_id in enumerate(friend_list['requested']):
        user = models.Users.objects.filter(user_id=friend_id).first()
        requested.append({
            'id': str(i),
            'name': user.user_id,
            'email': user.email,
            'status': 'offline'
        })

    return Response({
        'friends': friends,
        'pending': pending,
        'requested': requested
    }, status=HTTP_200_OK)

@api_view(['PUT'])
def Accept_Friend(request):
    current_user_id = request.data['user_id']
    target_user_id = request.data['target_user_id']

    current_user_friends = models.Friends.objects.filter(user_id=current_user_id).first()
    target_user_friends = models.Friends.objects.filter(user_id=target_user_id).first()
    
    current_user_friends.friend_list['pending'].remove(target_user_id)
    current_user_friends.friend_list['friends'].append(target_user_id)
    current_user_friends.save()
    
    target_user_friends.friend_list['requested'].remove(current_user_id)
    target_user_friends.friend_list['friends'].append(current_user_id)
    target_user_friends.save()
    
    return Response({'message': 'Friend request accepted'}, status=HTTP_200_OK)

@api_view(['PUT'])
def Reject_Friend(request):
    current_user_id = request.data['user_id']
    target_user_id = request.data['target_user_id']

    current_user_friends = models.Friends.objects.filter(user_id=current_user_id).first()
    target_user_friends = models.Friends.objects.filter(user_id=target_user_id).first()

    current_user_friends.friend_list['pending'].remove(target_user_id)
    current_user_friends.save()

    target_user_friends.friend_list['requested'].remove(current_user_id)
    target_user_friends.save()
    
    return Response({'message': 'Friend request rejected'}, status=HTTP_200_OK)

@api_view(['PUT'])
def Remove_Friend(request):
    current_user_id = request.data['user_id']
    target_user_id = request.data['target_user_id']
    
    # Get current user's friend list
    current_user_friends = models.Friends.objects.filter(user_id=current_user_id).first()
    if not current_user_friends:
        return Response({'error': 'User not found'}, status=HTTP_400_BAD_REQUEST)
    
    # Get target user's friend list
    target_user_friends = models.Friends.objects.filter(user_id=target_user_id).first()
    if not target_user_friends:
        return Response({'error': 'Target user not found'}, status=HTTP_400_BAD_REQUEST)
    
    # Check which list to remove from
    if target_user_id in current_user_friends.friend_list['friends']:
        # Remove from friends list
        current_user_friends.friend_list['friends'].remove(target_user_id)
        current_user_friends.save()
        
        # Also remove current user from target user's friends list
        if current_user_id in target_user_friends.friend_list['friends']:
            target_user_friends.friend_list['friends'].remove(current_user_id)
            target_user_friends.save()
            
        return Response({'message': 'Friend removed successfully'}, status=HTTP_200_OK)
    
    elif target_user_id in current_user_friends.friend_list['requested']:
        # Cancel friend request
        current_user_friends.friend_list['requested'].remove(target_user_id)
        current_user_friends.save()
        
        # Remove from target user's pending list
        if current_user_id in target_user_friends.friend_list['pending']:
            target_user_friends.friend_list['pending'].remove(current_user_id)
            target_user_friends.save()
            
        return Response({'message': 'Friend request canceled'}, status=HTTP_200_OK)
    
    elif target_user_id in current_user_friends.friend_list['pending']:
        # Reject friend request
        current_user_friends.friend_list['pending'].remove(target_user_id)
        current_user_friends.save()
        
        # Remove from target user's requested list
        if current_user_id in target_user_friends.friend_list['requested']:
            target_user_friends.friend_list['requested'].remove(current_user_id)
            target_user_friends.save()
            
        return Response({'message': 'Friend request rejected'}, status=HTTP_200_OK)
    
    return Response({'message': 'User not found in any friend list'}, status=HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def Send_Friend_Request(request):
    current_user_id = request.data['user_id']
    target_user_id = request.data['target_user_id']

    current_user_friends = models.Friends.objects.filter(user_id=current_user_id).first()
    target_user_friends = models.Friends.objects.filter(user_id=target_user_id).first()    

    current_user_friends.friend_list['requested'].append(target_user_id)
    current_user_friends.save()

    target_user_friends.friend_list['pending'].append(current_user_id)
    target_user_friends.save()

    return Response({'message': 'Friend request sent'}, status=HTTP_200_OK)