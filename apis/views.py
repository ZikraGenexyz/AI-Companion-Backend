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
import random
import string
from datetime import datetime

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
def Account_Init(request):
    account_id = request.data['account_id']
    email = request.data['email']

    if models.Parents_Accounts.objects.filter(account_id=account_id).first() is None:
        models.Parents_Accounts.objects.create(account_id=account_id, email=email)

    return Response({'message': 'Account initialized successfully'}, status=HTTP_200_OK)

@api_view(['POST'])
def Child_Init(request):
    username = request.data['username']
    isActive = True
    user_id = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=28))
    birth_date = str(datetime.now().year - int(request.data['age'])) + '-01-01'

    models.Children_Accounts.objects.create(account=None, user_id=user_id, isActive=isActive, user_info={
        "name": username,
        "gender": "",
        "birth_date": birth_date,
        "school": "",
        "energy_level": 0,
        "robot_type": 0,
        "robot_color": 0,
    })

    return Response({'message': 'Child initialized successfully', 'user_id': user_id}, status=HTTP_200_OK)

@api_view(['POST'])
def Child_Bind_Status(request):
    user_id = request.data['user_id']
    child = models.Children_Accounts.objects.filter(user_id=user_id).first()

    bind_status = False

    if child.account is not None:
        bind_status = True

    return Response({'bind_status': bind_status}, status=HTTP_200_OK)

@api_view(['DELETE'])
def ResetChat(request):
    models.Chat_History.objects.filter(user_id=request.data['user_id']).delete()
    return Response({'message': 'Chat reset successfully'}, status=HTTP_200_OK)

@api_view(['POST'])
def GetChat(request):
    chat = models.Chat_History.objects.filter(user_id=request.data['user_id'], isUser=True)
    summary = ''
    for c in chat:
        summary += c.text + ', '
    # summary = summary.rstrip(', ')

    summary += '[do not respond]'

    return Response({'summary': summary}, status=HTTP_200_OK)

@api_view(['PUT'])
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
    user_id = request.data['user_id']
    friend_list = models.Children_Accounts.objects.filter(user_id=user_id).first().friend_list

    friends = []
    pending = []
    requests = []

    for i, friend_id in enumerate(friend_list['friends']):
        user = models.Children_Accounts.objects.filter(user_id=friend_id).first()
        friends.append({
            'id': friend_id,
            'name': user.username,
            'status': 'online'
        })

    for i, friend_id in enumerate(friend_list['pending']):
        user = models.Children_Accounts.objects.filter(user_id=friend_id).first()
        pending.append({
            'id': friend_id,
            'name': user.username,
            'status': 'offline'
        })

    for i, friend_id in enumerate(friend_list['requests']):
        user = models.Children_Accounts.objects.filter(user_id=friend_id).first()
        requests.append({
            'id': friend_id,
            'name': user.username,
            'email': user.email,
            'status': 'offline'
        })

    return Response({
        'friends': friends,
        'pending': pending,
        'requests': requests
    }, status=HTTP_200_OK)

@api_view(['PUT'])
def Accept_Friend(request):
    current_user_id = request.data['user_id']
    target_user_id = request.data['target_user_id']

    current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
    target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()
    
    current_user_friends.friend_list['pending'].remove(target_user_id)
    current_user_friends.friend_list['friends'].append(target_user_id)
    current_user_friends.save()
    
    target_user_friends.friend_list['requests'].remove(current_user_id)
    target_user_friends.friend_list['friends'].append(current_user_id)
    target_user_friends.save()
    
    return Response({'message': 'Friend request accepted'}, status=HTTP_200_OK)

@api_view(['PUT'])
def Reject_Friend(request):
    current_user_id = request.data['user_id']
    target_user_id = request.data['target_user_id']

    current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
    target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()

    current_user_friends.friend_list['pending'].remove(target_user_id)
    current_user_friends.save()

    target_user_friends.friend_list['requests'].remove(current_user_id)
    target_user_friends.save()
    
    return Response({'message': 'Friend request rejected'}, status=HTTP_200_OK)

@api_view(['PUT'])
def Remove_Friend(request):
    current_user_id = request.data['user_id']
    target_user_id = request.data['target_user_id']
    
    # Get current user's friend list
    current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
    if not current_user_friends:
        return Response({'error': 'User not found'}, status=HTTP_400_BAD_REQUEST)
    
    # Get target user's friend list
    target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()
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
    
    elif target_user_id in current_user_friends.friend_list['requests']:
        # Cancel friend request
        current_user_friends.friend_list['requests'].remove(target_user_id)
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
        
        # Remove from target user's requests list
        if current_user_id in target_user_friends.friend_list['requests']:
            target_user_friends.friend_list['requests'].remove(current_user_id)
            target_user_friends.save()
            
        return Response({'message': 'Friend request rejected'}, status=HTTP_200_OK)
    
    return Response({'message': 'User not found in any friend list'}, status=HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def Send_Friend_Request(request):
    current_user_id = request.data['user_id']
    target_user_id = request.data['target_user_id']

    current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
    target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()    

    current_user_friends.friend_list['requests'].append(target_user_id)
    current_user_friends.save()

    target_user_friends.friend_list['pending'].append(current_user_id)
    target_user_friends.save()

    return Response({'message': 'Friend request sent'}, status=HTTP_200_OK)

@api_view(['POST'])
def Search_User(request):
    users = models.Children_Accounts.objects.filter(username__icontains=request.data['query'])
    
    user_list = []

    for i, user in enumerate(users):
        if user.account.user_id != request.data['user_id']:
            user_list.append({
                'id': user.account.user_id,
                'name': user.username,
                'email': user.email
            })

    return Response({"users": user_list}, status=HTTP_200_OK)

@api_view(['PUT'])
def Cancel_Friend_Request(request):
    current_user_id = request.data['user_id']
    target_user_id = request.data['target_user_id']

    current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
    target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()

    current_user_friends.friend_list['requests'].remove(target_user_id)
    current_user_friends.save()

    target_user_friends.friend_list['pending'].remove(current_user_id)
    target_user_friends.save()

    return Response({"message": "Friend request canceled"}, status=HTTP_200_OK)

@api_view(['POST'])
def Get_Account_Users(request):
    account_id = request.data['account_id']
    users = models.Children_Accounts.objects.filter(account=models.Parents_Accounts.objects.filter(account_id=account_id).first())

    user_list = []

    for user in users:
        user_list.append({
            'id': user.user_id,
            'name': user.username
        })

    return Response({"users": user_list}, status=HTTP_200_OK)

@api_view(['POST'])
def Add_User(request):
    account_id = request.data['account_id']
    username = request.data['username']
    user_id = ''

    user_id = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=28))

    models.Children_Accounts.objects.create(account=models.Parents_Accounts.objects.filter(account_id=account_id).first(), user_id=user_id, username=username)

    return Response({'message': 'User initialized successfully', 'user_id': user_id}, status=HTTP_200_OK)

@api_view(['DELETE'])
def Remove_User(request):
    user_id = request.data['user_id']
    models.Children_Accounts.objects.filter(user_id=user_id).delete()

    return Response({'message': 'User removed successfully'}, status=HTTP_200_OK)

@api_view(['PUT'])
def Update_User(request):
    user_id = request.data['user_id']
    username = request.data['username']

    user = models.Children_Accounts.objects.filter(user_id=user_id).first()
    user.username = username
    user.save()

    return Response({'message': 'User updated successfully'}, status=HTTP_200_OK)

@api_view(['GET'])
def Get_Assistant_ID(request):
    nekokuma = os.getenv('NEKOKUMA_ID')

    return Response({'nekokuma': nekokuma}, status=HTTP_200_OK)

@api_view(['POST'])
def Create_Bind_OTP(request):
    user_id = request.data['user_id']
    otp = ''.join(random.choices(string.digits, k=4))

    child = models.Children_Accounts.objects.filter(user_id=user_id).first()
    child.bind_otp = otp
    child.save()

    return Response({'message': 'Bind OTP created successfully', 'otp': otp}, status=HTTP_200_OK)

@api_view(['POST'])
def Verify_Bind_OTP(request):
    account_id = request.data['account_id']
    otp = request.data['otp']

    user = models.Children_Accounts.objects.filter(bind_otp=otp).first()

    if user is not None:
        user.bind_otp = None
        user.account = models.Parents_Accounts.objects.filter(account_id=account_id).first()
        user.save()

        return Response({'message': 'Bind OTP verified successfully'}, status=HTTP_200_OK)
    else:
        return Response({'message': 'Bind OTP verification failed'}, status=HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def Get_Children(request):
    users = models.Children_Accounts.objects.filter(account=models.Parents_Accounts.objects.filter(account_id=request.data['account_id']).first())
    user_list = []

    for user in users:
        gender = None if user.user_info['gender'] == "" else user.user_info['gender']
        birth_date = None if user.user_info['birth_date'] == "" else user.user_info['birth_date']
        school = None if user.user_info['school'] == "" else user.user_info['school']

        user_list.append({
            'id': user.user_id,
            'name': user.user_info['name'],
            'gender': gender,
            'birth_date': birth_date,
            'school': school,
            'robot_type': user.user_info['robot_type'],
            'robot_color': user.user_info['robot_color'],
            'energy_level': user.user_info['energy_level'],
            'total_missions': len(user.notification['missions']),
            'completed_missions': 0,
        })

    return Response({'children': user_list}, status=HTTP_200_OK)

@api_view(['POST'])
def Edit_Child(request):
    user_id = request.data['user_id']
    username = request.data['username']
    gender = request.data['gender']
    birth_date = request.data['birth_date']
    school = request.data['school']

    child = models.Children_Accounts.objects.filter(user_id=user_id).first()
    child.user_info = {
        "name": username,
        "gender": gender,
        "birth_date": birth_date.replace(' 00:00:00.000', ''),
        "school": school,
        "energy_level": child.user_info['energy_level'],
        "robot_type": child.user_info['robot_type'],
        "robot_color": child.user_info['robot_color'],
    }
    child.save()

    return Response({'message': 'Child updated successfully'}, status=HTTP_200_OK)

@api_view(['POST'])
def Get_Love_Notes(request):
    print(request.data)
    try:
        user_id = request.data['user_id']
        getUncompleted = True if request.data['get_uncompleted'] == 'true' else False
    except:
        user_id = request.data['message']['toolCalls'][0]['function']['arguments']['user_id']
        getUncompleted = True

    child = models.Children_Accounts.objects.filter(user_id=user_id).first()
    love_notes = child.notification['love_notes']

    if getUncompleted:
        notes = f'There is {len(love_notes)} love notes for you. \n'
        uncompleted_notes_indices = []
        
        for i, note in enumerate(love_notes):
            if not note['completed']:
                notes += f'{note["note"]}, \n'
                uncompleted_notes_indices.append(i)
                
                # Mark the note as completed
                love_notes[i]['completed'] = True
        
        # Save the changes to the database if any notes were marked as completed
        if uncompleted_notes_indices:
            child.save()
            
        notes = notes.rstrip(', \n')
        return Response({"results":[{"result": notes, "toolCallId": request.data['message']['toolCalls'][0]['id']}]}, status=HTTP_200_OK)
    else:
        return Response({'love_notes': love_notes}, status=HTTP_200_OK)

@api_view(['POST'])
def Add_Love_Note(request):
    user_id = request.data['user_id']
    love_note = request.data['love_note']

    child = models.Children_Accounts.objects.filter(user_id=user_id).first()
    child.notification['love_notes'].append({
        'note': love_note,
        'completed': False
    })
    child.save()

    return Response({'message': 'Love note added successfully'}, status=HTTP_200_OK)

@api_view(['POST'])
def Remove_Love_Note(request):
    user_id = request.data['user_id']
    index = int(request.data['index'])

    child = models.Children_Accounts.objects.filter(user_id=user_id).first()
    child.notification['love_notes'].pop(index)
    child.save()

    return Response({'message': 'Love note removed successfully'}, status=HTTP_200_OK)

@api_view(['POST'])
def Edit_Love_Note(request):
    user_id = request.data['user_id']
    index = int(request.data['index'])
    love_note = request.data['love_note']

    child = models.Children_Accounts.objects.filter(user_id=user_id).first()
    child.notification['love_notes'][index]['note'] = love_note
    child.save()

    return Response({'message': 'Love note updated successfully'}, status=HTTP_200_OK)

@api_view(['POST'])
def Unbind_Children_Account(request):
    user_id = request.data['user_id']

    user = models.Children_Accounts.objects.filter(user_id=user_id).first()
    user.account = None
    user.save()

    return Response({'message': 'Account unbound successfully'}, status=HTTP_200_OK)

@api_view(['POST'])
def Bind_Children_Account(request):
    user_id = request.data['user_id']
    account_id = request.data['account_id']

    user = models.Children_Accounts.objects.filter(user_id=user_id).first()
    user.account = models.Parents_Accounts.objects.filter(account_id=account_id).first()
    user.save()

    return Response({'message': 'Account bound successfully'}, status=HTTP_200_OK)