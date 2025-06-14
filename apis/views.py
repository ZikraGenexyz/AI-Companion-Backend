# Re-export views from their respective modules
# from .api_views.account_views import *
# from .api_views.chat_views import *
# from .api_views.mission_views import *
# from .api_views.social_views import *
# from .api_views.ai_views import *

# from django.shortcuts import render
# from companion_app import models
# from .serializers import ChatsSerializer
# from rest_framework import generics
# from rest_framework.response import Response
# from django.contrib.auth import authenticate
# from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
# from django.views.decorators.csrf import csrf_exempt, csrf_protect
# from django.utils.decorators import method_decorator
# from rest_framework.decorators import api_view
# from django.contrib.auth.models import User
# import logging
# import json
# import base64
# import os
# from dotenv import load_dotenv
# from django.http import JsonResponse
# from cartesia import Cartesia
# import groq
# from serpapi import GoogleSearch
# import requests
# import random
# import string
# from datetime import datetime
# # from .firebase_config import storage
# import uuid
# import tempfile
# from urllib.parse import urlparse, unquote
# from google.cloud import storage
# from google.oauth2 import service_account
# from openai import OpenAI

# # Load environment variables
# load_dotenv()

# # Initialize Groq client
# groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))

# # Initialize Cartesia client
# cartesia_client = Cartesia(api_key=os.getenv('CARTESIA_API_KEY'))

# # Initialize Firebase Storage
# creds_dict = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
# credentials = service_account.Credentials.from_service_account_info(creds_dict)
# client = storage.Client(credentials=credentials)
# bucket = client.bucket(os.getenv("FIREBASE_BUCKET"))


# # ------------------------------------------------------------- #
# #                       Parent Account APIs
# # ------------------------------------------------------------- #

# @api_view(['PUT'])
# def Account_Init(request):
#     account_id = request.data['account_id']
#     email = request.data['email']
#     username = request.data['username']

#     if models.Parents_Accounts.objects.filter(account_id=account_id).first() is None:
#         models.Parents_Accounts.objects.create(account_id=account_id, 
#                                                email=email, 
#                                                username=username, 
#                                                date_of_birth=None, 
#                                                phone_number=None, 
#                                                relation=None)

#     return Response({'message': 'Account initialized successfully'}, status=HTTP_200_OK)

# @api_view(['PUT'])
# def Account_Update(request):
#     account_id = request.data['account_id']
#     username = request.data['username']
#     date_of_birth = request.data['date_of_birth']
#     phone_number = request.data['phone_number']
#     relation = request.data['relation']

#     models.Parents_Accounts.objects.filter(account_id=account_id).update(
#         username=username, 
#         date_of_birth=date_of_birth if date_of_birth != '' else None, 
#         phone_number=phone_number if phone_number != '' else None, 
#         relation=relation if relation != '' else None)

#     return Response({'message': 'Account updated successfully'}, status=HTTP_200_OK)

# @api_view(['GET'])
# def Account_Get_Info(request):
#     account_id = request.GET.get('account_id')
#     account = models.Parents_Accounts.objects.filter(account_id=account_id).first()

#     return Response({
#         'username': account.username, 
#         'date_of_birth': account.date_of_birth, 
#         'phone_number': account.phone_number, 
#         'relation': account.relation
#     }, status=HTTP_200_OK)

# @api_view(['DELETE'])
# def Account_Delete(request):
#     account_id = request.data['account_id']
#     models.Parents_Accounts.objects.filter(account_id=account_id).delete()

#     return Response({'message': 'Account deleted successfully'}, status=HTTP_200_OK)

# # ------------------------------------------------------------- #
# #                       Child Account APIs
# # ------------------------------------------------------------- #

# @api_view(['POST'])
# def Child_Init(request):
#     username = request.data['username']
#     robot_type = request.data['robot_type']
#     robot_color = request.data['robot_color']
#     isActive = True
#     user_id = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=28))
#     birth_date = str(datetime.now().year - int(request.data['age'])) + '-01-01'

#     models.Children_Accounts.objects.create(account=None, user_id=user_id, isActive=isActive, user_info={
#         "name": username,
#         "gender": "",
#         "birth_date": birth_date,
#         "school": "",
#         "energy_level": 0,
#         "robot_type": robot_type,
#         "robot_color": robot_color,
#     })

#     return Response({'message': 'Child initialized successfully', 'user_id': user_id}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Child_Bind_Status(request):
#     user_id = request.data['user_id']
#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()

#     bind_status = False

#     if child.account is not None:
#         bind_status = True

#     return Response({'bind_status': bind_status}, status=HTTP_200_OK)

# # ------------------------------------------------------------- #
# #                       Chats APIs
# # ------------------------------------------------------------- #

# @api_view(['DELETE'])
# def ResetChat(request):
#     models.Chat_History.objects.filter(user_id=request.data['user_id']).delete()
#     return Response({'message': 'Chat reset successfully'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def GetChat(request):
#     chat = models.Chat_History.objects.filter(user_id=request.data['user_id'], isUser=True)
#     summary = ''
#     for c in chat:
#         summary += c.text + ', '
#     # summary = summary.rstrip(', ')

#     summary += '[do not respond]'

#     return Response({'summary': summary}, status=HTTP_200_OK)

# @api_view(['PUT'])
# def AddChat(request):
#     text = request.data['text']
#     user_id = request.data['user_id']
#     isUser = True if request.data['isUser'] == 'true' else False

#     chat_history = models.Chat_History.objects.filter(user_id=user_id).last()

#     if chat_history is not None:
#         if chat_history.isUser == isUser:
#             chat_history.text = text
#             chat_history.save()
#         else:
#             models.Chat_History.objects.create(text=text, user_id=user_id, isUser=isUser)
#     else:
#         models.Chat_History.objects.create(text=text, user_id=user_id, isUser=isUser)
    
#     return Response({'message': 'Chat added successfully'}, status=HTTP_200_OK)

# # ------------------------------------------------------------- #
# #                       AI APIs
# # ------------------------------------------------------------- #

# @api_view(['POST'])
# def GoogleSearchApi(request):
#     search = GoogleSearch({
#         "q": request.data['query'], 
#         "location": "Indonesia, Jakarta",
#         "api_key": os.getenv('GOOGLE_API_KEY')
#     })

#     result = search.get_dict()
#     result = result['search_results']['related_questions'][0]['snippet']

#     return Response({'search_results': result}, status=HTTP_200_OK)

# @api_view(['POST'])
# def GenerateImage(request):

#     engine_id = "stable-diffusion-v1-6"
#     api_host = os.getenv('API_HOST', 'https://api.stability.ai')
#     api_key = os.getenv('STABILITY_API_KEY')

#     if api_key is None:
#         raise Exception("Missing Stability API key.")

#     response = requests.post(
#         f"{api_host}/v1/generation/{engine_id}/text-to-image",
#         headers={
#             "Content-Type": "application/json",
#             "Accept": "application/json",
#             "Authorization": f"Bearer {api_key}"
#         },
#         json={
#             "text_prompts": [
#                 {
#                     "text": request.data['prompt']
#                 }
#             ],
#             "cfg_scale": 7,
#             "height": 1024,
#             "width": 576,
#             "samples": 1,
#             "steps": 30,
#         },
#     )

#     if response.status_code == 200:
#         data = response.json()

#         image_data = data['artifacts'][0]['base64']

#         # Encode binary image data to base64
#         # image_data = base64.b64encode(response.content).decode('utf-8')
        
#         return Response({
#             'success': True,
#             'image': image_data,
#             # 'content_type': response.headers.get('Content-Type', 'image/jpeg')
#         }, status=HTTP_200_OK)
#     else:
#         return Response({
#             'success': False, 
#             'error': response.json()
#         }, status=HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def Get_Friend_List(request):
#     user_id = request.data['user_id']
#     friend_list = models.Children_Accounts.objects.filter(user_id=user_id).first().friend_list

#     friends = []
#     pending = []
#     requests = []

#     for i, friend_id in enumerate(friend_list['friends']):
#         user = models.Children_Accounts.objects.filter(user_id=friend_id).first()
#         friends.append({
#             'id': friend_id,
#             'name': user.username,
#             'status': 'online'
#         })

#     for i, friend_id in enumerate(friend_list['pending']):
#         user = models.Children_Accounts.objects.filter(user_id=friend_id).first()
#         pending.append({
#             'id': friend_id,
#             'name': user.username,
#             'status': 'offline'
#         })

#     for i, friend_id in enumerate(friend_list['requests']):
#         user = models.Children_Accounts.objects.filter(user_id=friend_id).first()
#         requests.append({
#             'id': friend_id,
#             'name': user.username,
#             'email': user.email,
#             'status': 'offline'
#         })

#     return Response({
#         'friends': friends,
#         'pending': pending,
#         'requests': requests
#     }, status=HTTP_200_OK)

# @api_view(['PUT'])
# def Accept_Friend(request):
#     current_user_id = request.data['user_id']
#     target_user_id = request.data['target_user_id']

#     current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
#     target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()
    
#     current_user_friends.friend_list['pending'].remove(target_user_id)
#     current_user_friends.friend_list['friends'].append(target_user_id)
#     current_user_friends.save()
    
#     target_user_friends.friend_list['requests'].remove(current_user_id)
#     target_user_friends.friend_list['friends'].append(current_user_id)
#     target_user_friends.save()
    
#     return Response({'message': 'Friend request accepted'}, status=HTTP_200_OK)

# @api_view(['PUT'])
# def Reject_Friend(request):
#     current_user_id = request.data['user_id']
#     target_user_id = request.data['target_user_id']

#     current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
#     target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()

#     current_user_friends.friend_list['pending'].remove(target_user_id)
#     current_user_friends.save()

#     target_user_friends.friend_list['requests'].remove(current_user_id)
#     target_user_friends.save()
    
#     return Response({'message': 'Friend request rejected'}, status=HTTP_200_OK)

# @api_view(['PUT'])
# def Remove_Friend(request):
#     current_user_id = request.data['user_id']
#     target_user_id = request.data['target_user_id']
    
#     # Get current user's friend list
#     current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
#     if not current_user_friends:
#         return Response({'error': 'User not found'}, status=HTTP_400_BAD_REQUEST)
    
#     # Get target user's friend list
#     target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()
#     if not target_user_friends:
#         return Response({'error': 'Target user not found'}, status=HTTP_400_BAD_REQUEST)
    
#     # Check which list to remove from
#     if target_user_id in current_user_friends.friend_list['friends']:
#         # Remove from friends list
#         current_user_friends.friend_list['friends'].remove(target_user_id)
#         current_user_friends.save()
        
#         # Also remove current user from target user's friends list
#         if current_user_id in target_user_friends.friend_list['friends']:
#             target_user_friends.friend_list['friends'].remove(current_user_id)
#             target_user_friends.save()
            
#         return Response({'message': 'Friend removed successfully'}, status=HTTP_200_OK)
    
#     elif target_user_id in current_user_friends.friend_list['requests']:
#         # Cancel friend request
#         current_user_friends.friend_list['requests'].remove(target_user_id)
#         current_user_friends.save()
        
#         # Remove from target user's pending list
#         if current_user_id in target_user_friends.friend_list['pending']:
#             target_user_friends.friend_list['pending'].remove(current_user_id)
#             target_user_friends.save()
            
#         return Response({'message': 'Friend request canceled'}, status=HTTP_200_OK)
    
#     elif target_user_id in current_user_friends.friend_list['pending']:
#         # Reject friend request
#         current_user_friends.friend_list['pending'].remove(target_user_id)
#         current_user_friends.save()
        
#         # Remove from target user's requests list
#         if current_user_id in target_user_friends.friend_list['requests']:
#             target_user_friends.friend_list['requests'].remove(current_user_id)
#             target_user_friends.save()
            
#         return Response({'message': 'Friend request rejected'}, status=HTTP_200_OK)
    
#     return Response({'message': 'User not found in any friend list'}, status=HTTP_400_BAD_REQUEST)

# @api_view(['PUT'])
# def Send_Friend_Request(request):
#     current_user_id = request.data['user_id']
#     target_user_id = request.data['target_user_id']

#     current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
#     target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()    

#     current_user_friends.friend_list['requests'].append(target_user_id)
#     current_user_friends.save()

#     target_user_friends.friend_list['pending'].append(current_user_id)
#     target_user_friends.save()

#     return Response({'message': 'Friend request sent'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Search_User(request):
#     users = models.Children_Accounts.objects.filter(username__icontains=request.data['query'])
    
#     user_list = []

#     for i, user in enumerate(users):
#         if user.account.user_id != request.data['user_id']:
#             user_list.append({
#                 'id': user.account.user_id,
#                 'name': user.username,
#                 'email': user.email
#             })

#     return Response({"users": user_list}, status=HTTP_200_OK)

# @api_view(['PUT'])
# def Cancel_Friend_Request(request):
#     current_user_id = request.data['user_id']
#     target_user_id = request.data['target_user_id']

#     current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
#     target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()

#     current_user_friends.friend_list['requests'].remove(target_user_id)
#     current_user_friends.save()

#     target_user_friends.friend_list['pending'].remove(current_user_id)
#     target_user_friends.save()

#     return Response({"message": "Friend request canceled"}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Get_Account_Users(request):
#     account_id = request.data['account_id']
#     users = models.Children_Accounts.objects.filter(account=models.Parents_Accounts.objects.filter(account_id=account_id).first())

#     user_list = []

#     for user in users:
#         user_list.append({
#             'id': user.user_id,
#             'name': user.username
#         })

#     return Response({"users": user_list}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Add_User(request):
#     account_id = request.data['account_id']
#     username = request.data['username']
#     user_id = ''

#     user_id = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=28))

#     models.Children_Accounts.objects.create(account=models.Parents_Accounts.objects.filter(account_id=account_id).first(), user_id=user_id, username=username)

#     return Response({'message': 'User initialized successfully', 'user_id': user_id}, status=HTTP_200_OK)

# @api_view(['DELETE'])
# def Remove_User(request):
#     user_id = request.data['user_id']
#     models.Children_Accounts.objects.filter(user_id=user_id).delete()

#     return Response({'message': 'User removed successfully'}, status=HTTP_200_OK)

# @api_view(['PUT'])
# def Update_User(request):
#     user_id = request.data['user_id']
#     username = request.data['username']

#     user = models.Children_Accounts.objects.filter(user_id=user_id).first()
#     user.username = username
#     user.save()

#     return Response({'message': 'User updated successfully'}, status=HTTP_200_OK)

# @api_view(['GET'])
# def Get_Assistant_ID(request):
#     nekokuma = os.getenv('NEKOKUMA_ID')

#     return Response({'nekokuma': nekokuma}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Create_Bind_OTP(request):
#     user_id = request.data['user_id']
#     otp = ''.join(random.choices(string.digits, k=4))

#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()
#     child.bind_otp = otp
#     child.save()

#     return Response({'message': 'Bind OTP created successfully', 'otp': otp}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Verify_Bind_OTP(request):
#     account_id = request.data['account_id']
#     otp = request.data['otp']

#     user = models.Children_Accounts.objects.filter(bind_otp=otp).first()

#     if user is not None:
#         user.bind_otp = None
#         user.account = models.Parents_Accounts.objects.filter(account_id=account_id).first()
#         user.save()

#         return Response({'message': 'Bind OTP verified successfully'}, status=HTTP_200_OK)
#     else:
#         return Response({'message': 'Bind OTP verification failed'}, status=HTTP_400_BAD_REQUEST)
    
# @api_view(['POST'])
# def Get_Children(request):
#     users = models.Children_Accounts.objects.filter(account=models.Parents_Accounts.objects.filter(account_id=request.data['account_id']).first())
#     user_list = []

#     for user in users:
#         completed_notes = sum(1 for note in user.notification['love_notes'] if note.get('completed', False))
#         completed_missions = sum(1 for mission in user.notification['missions'] if mission.get('completed', False))

#         user_list.append({
#           'id': user.user_id,
#           'user_info': user.user_info,
#           'missions': {'completed': completed_missions, 'total': len(user.notification['missions'])},
#           'loveNotes': {'completed': completed_notes, 'total': len(user.notification['love_notes'])},
#         })

#     return Response({'children': user_list}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Edit_Child(request):
#     user_id = request.data['user_id']
#     username = request.data['username']
#     gender = request.data['gender']
#     birth_date = request.data['birth_date']
#     school = request.data['school']
#     robot_type = request.data['robot_type']
#     robot_color = request.data['robot_color']

#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()

#     username = username if len(username) > 0 else child.user_info['name']
#     gender = gender if len(gender) > 0 else child.user_info['gender']
#     birth_date = birth_date.replace(' 00:00:00.000', '') if len(birth_date) > 0 else child.user_info['birth_date']
#     school = school if len(school) > 0 else child.user_info['school']
#     robot_type = robot_type if len(robot_type) > 0 else child.user_info['robot_type']
#     robot_color = robot_color if len(robot_color) > 0 else child.user_info['robot_color']

#     child.user_info = {
#         "name": username,
#         "gender": gender,
#         "birth_date": birth_date,
#         "school": school,
#         "energy_level": child.user_info['energy_level'],
#         "robot_type": robot_type,
#         "robot_color": robot_color,
#     }
#     child.save()

#     return Response({'message': 'Child updated successfully'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Get_Love_Notes(request):
#     print(request.data)
#     try:
#         user_id = request.data['user_id']
#         getUncompleted = True if request.data['get_uncompleted'] == 'true' else False
#     except:
#         user_id = request.data['message']['toolCalls'][0]['function']['arguments']['user_id']
#         getUncompleted = True

#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()
#     love_notes = child.notification['love_notes']

#     if getUncompleted:
#         notes = f'There is {len(love_notes)} love notes for you. \n'
#         uncompleted_notes_indices = []
        
#         for i, note in enumerate(love_notes):
#             if not note['completed']:
#                 notes += f'{note["note"]}, \n'
#                 uncompleted_notes_indices.append(i)
                
#                 # Mark the note as completed
#                 love_notes[i]['completed'] = True
        
#         # Save the changes to the database if any notes were marked as completed
#         if uncompleted_notes_indices:
#             child.save()
            
#         notes = notes.rstrip(', \n')
#         return Response({"results":[{"result": notes, "toolCallId": request.data['message']['toolCalls'][0]['id']}]}, status=HTTP_200_OK)
#     else:
#         return Response({'love_notes': love_notes}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Add_Love_Note(request):
#     user_id = request.data['user_id']
#     love_note = request.data['love_note']

#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()
#     child.notification['love_notes'].append({
#         'note': love_note,
#         'completed': False
#     })
#     child.save()

#     return Response({'message': 'Love note added successfully'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Remove_Love_Note(request):
#     user_id = request.data['user_id']
#     index = int(request.data['index'])

#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()
#     child.notification['love_notes'].pop(index)
#     child.save()

#     return Response({'message': 'Love note removed successfully'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Edit_Love_Note(request):
#     user_id = request.data['user_id']
#     index = int(request.data['index'])
#     love_note = request.data['love_note']

#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()
#     child.notification['love_notes'][index]['note'] = love_note
#     child.save()

#     return Response({'message': 'Love note updated successfully'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Unbind_Children_Account(request):
#     user_id = request.data['user_id']

#     user = models.Children_Accounts.objects.filter(user_id=user_id).first()
#     user.account = None
#     user.save()

#     return Response({'message': 'Account unbound successfully'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Bind_Children_Account(request):
#     user_id = request.data['user_id']
#     account_id = request.data['account_id']

#     user = models.Children_Accounts.objects.filter(user_id=user_id).first()
#     user.account = models.Parents_Accounts.objects.filter(account_id=account_id).first()
#     user.save()

#     return Response({'message': 'Account bound successfully'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Get_Missions(request):
#     user_id = request.data['user_id']
#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()
#     missions = child.notification['missions']

#     return Response({'missions': missions}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Add_Mission(request):
#     user_id = request.data['user_id']
#     mission_type = request.data['mission_type']
#     mission_title = request.data['mission_title']
#     mission_due_date = request.data['mission_due_date']
#     mission_due_time = request.data['mission_due_time']
#     mission_repeat = request.data['mission_repeat']
        
#     mission_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

#     mission_data = {
#         'id': mission_id,
#         'title': mission_title,
#         'due_date': mission_due_date,
#         'due_time': mission_due_time,
#         'category': mission_type,
#         'completed': False,
#         'repeat': mission_repeat,
#         'gpt_response': None,
#     }
    
#     if mission_type == 'Homework':
#         mission_data['instructions'] = request.data['mission_instructions']
#         mission_data['confirmation'] = False
        
#         # Handle all file attachments from request.FILES
#         if request.FILES:
#             print('Attachments found')

#             attachment_urls = []
            
#             # Process each file in request.FILES
#             for file_key, attachment_file in request.FILES.items():
#                 # Generate a unique file name
#                 file_extension = attachment_file.name.split('.')[-1]
#                 unique_filename = f"mission_attachments/{user_id}/{str(uuid.uuid4())}.{file_extension}"
                
#                 # Create a temporary file
#                 # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#                 #     for chunk in attachment_file.chunks():
#                 #         temp_file.write(chunk)
#                 #     temp_file_path = temp_file.name
                
#                 # Upload the temporary file to Firebase storage
#                 # storage.child(unique_filename).put(temp_file_path)
#                 blob = bucket.blob(unique_filename)
#                 blob.upload_from_file(
#                     attachment_file.file,
#                     content_type=attachment_file.content_type
#                 )
                
#                 # Get the download URL
#                 blob.make_public()
#                 attachment_url = blob.public_url
                
#                 # Add the URL to the list
#                 attachment_urls.append(attachment_url)
                
#                 # Delete the temporary file
#                 # os.remove(temp_file_path)
            
#             # Add all URLs to the mission data
#             mission_data['attachments'] = attachment_urls
#         else:
#             print('No attachments')

#     # Get the child and add the mission
#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()
#     child.notification['missions'].append(mission_data)
#     child.save()
    
#     return Response({'message': 'Mission added successfully'}, status=HTTP_201_CREATED)

# @api_view(['POST'])
# def Complete_Mission(request):
#     try:
#         user_id = request.data['user_id']
#         mission_id = request.data['mission_id']

#         child = models.Children_Accounts.objects.filter(user_id=user_id).first()
#         for mission in child.notification['missions']:
#             if mission['id'] == mission_id:
#                 mission['completed'] = True
#                 mission['gpt_response'] = None
#                 mission['confirmation'] = False
#                 break
#         child.save()
#     except:
#         user_id = request.data['message']['toolCalls'][0]['function']['arguments']['user_id']
#         mission_id = request.data['message']['toolCalls'][0]['function']['arguments']['mission_id']

#         child = models.Children_Accounts.objects.filter(user_id=user_id).first()
#         for mission in child.notification['missions']:
#             if mission['id'] == mission_id:
#                 mission['confirmation'] = True
#                 break
#         child.save()
    
#     return Response({'message': 'Mission completed successfully'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Edit_Mission(request):
#     user_id = request.data['user_id']
#     mission_id = request.data['mission_id']
#     mission_type = request.data['mission_type']
#     mission_title = request.data['mission_title']
#     mission_due_date = request.data['mission_due_date']
#     mission_due_time = request.data['mission_due_time']
#     mission_repeat = request.data['mission_repeat'] 

#     try:
#         mission_attachments_urls = json.loads(request.data.get('attachment_urls', '[]'))
#     except:
#         mission_attachments_urls = None
    
#     if mission_type == 'Homework':
#         mission_instructions = request.data['mission_instructions']
    
#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()
    
#     # Find the mission and delete any attachments from Firebase
#     missions = child.notification['missions']
#     existing_attachments = []
    
#     for i, mission in enumerate(missions):
#         if mission['id'] == mission_id:
#             # Save existing attachments that weren't deleted
#             if 'attachments' in mission and mission['attachments']:
#                 for attachment_url in mission['attachments']:
#                     if mission_attachments_urls and attachment_url in mission_attachments_urls:
#                         existing_attachments.append(attachment_url)
#                         continue
#                     # Extract the file path from the URL and delete from storage
#                     try:
#                         # Extract the storage path from URL
#                         print("deleting", attachment_url)
#                         # Parse the URL to get just the path component
#                         # URL format: https://firebasestorage.googleapis.com/v0/b/BUCKET/o/PATH?alt=media...
#                         if 'https://storage.googleapis.com/companion-app-1b431.firebasestorage.app/' in attachment_url:
#                             storage_path = attachment_url.replace('https://storage.googleapis.com/companion-app-1b431.firebasestorage.app/', '')
#                             print("storage path:", storage_path)
                            
#                             # Use the child() method to create reference and then delete
#                             # storage.child(storage_path).delete(token=None)
#                             blob = bucket.blob(storage_path)
#                             blob.delete()
#                         else:
#                             print(f"Invalid URL format: {attachment_url}")
#                     except Exception as e:
#                         print(f"Error deleting file from Firebase: {e}")
            
#             # Remove the mission from the list
#             del missions[i]
#             break
    
#     # Create a new mission with updated data
#     new_mission = {
#         'id': mission_id,
#         'title': mission_title,
#         'due_date': mission_due_date,
#         'due_time': mission_due_time,
#         'repeat': mission_repeat,
#         'category': mission_type,
#         'completed': False
#     }
    
#     if mission_type == 'Homework':
#         new_mission['instructions'] = mission_instructions
#         new_mission['confirmation'] = False
#         new_mission['gpt_response'] = None
        
#         # Handle all file attachments from request.FILES
#         if request.FILES:
#             print('New attachments found')
#             attachment_urls = existing_attachments
            
#             # Process each file in request.FILES
#             for file_key, attachment_file in request.FILES.items():
#                 # Generate a unique file name
#                 file_extension = attachment_file.name.split('.')[-1]
#                 unique_filename = f"mission_attachments/{user_id}/{str(uuid.uuid4())}.{file_extension}"
                
#                 # Create a temporary file
#                 # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#                 #     for chunk in attachment_file.chunks():
#                 #         temp_file.write(chunk)
#                 #     temp_file_path = temp_file.name
                
#                 # Upload the temporary file to Firebase storage
#                 # storage.child(unique_filename).put(temp_file_path)
#                 blob = bucket.blob(unique_filename)
#                 blob.upload_from_file(
#                     attachment_file.file,
#                     content_type=attachment_file.content_type
#                 )
                
#                 # Get the download URL
#                 blob.make_public()
#                 attachment_url = blob.public_url
                
#                 # Add the URL to the list
#                 attachment_urls.append(attachment_url)
                
#                 # Delete the temporary file
#                 # os.remove(temp_file_path)
            
#             # Add all URLs to the mission data
#             new_mission['attachments'] = attachment_urls
#         elif existing_attachments:
#             # Keep existing attachments that weren't deleted
#             new_mission['attachments'] = existing_attachments
    
#     # Add the new mission back to the list
#     child.notification['missions'].append(new_mission)
#     child.save()

#     return Response({'message': 'Mission updated successfully'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Delete_Mission(request):
#     user_id = request.data['user_id']
#     mission_id = request.data['mission_id']

#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()
#     child.notification['missions'] = [mission for mission in child.notification['missions'] if mission['id'] != mission_id]
#     child.save()

#     return Response({'message': 'Mission deleted successfully'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Check_Homework_Completion(request):
#     user_id = request.data['user_id']
#     mission_id = request.data['mission_id']

#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()

#     current_mission = next((mission for mission in child.notification['missions'] if mission['id'] == mission_id), None)

#     if current_mission['confirmation'] == True:
#         return Response({'status': 'Completed'}, status=HTTP_200_OK)
#     else:
#         return Response({'status': 'Not Completed'}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Get_Child_Info(request):
#     user_id = request.data['user_id']
#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()

#     mission_list = child.notification['missions']
#     love_note_list = child.notification['love_notes']
#     user_info = child.user_info

#     return Response({
#         'missions': mission_list, 
#         'love_notes': love_note_list, 
#         'user_info': user_info}, status=HTTP_200_OK)

# def Get_GPT_Response(prompt, image_urls, max_tokens):
#     # Build content array starting with text
#     api_key = os.getenv('OPENAI_API_KEY')
#     client = OpenAI(api_key=api_key)
#     content = [
#         {"type": "input_text", "text": prompt},
#     ]

#     # Add each image URL or base64 to the content array
#     for image_url in image_urls:
#         content.append({"type": "input_image", "image_url": f"{image_url}"})

#     response = client.responses.create(
#         model="gpt-4o-mini",
#         input=[
#             {
#                 "role": "user",
#                 "content": content,
#             }
#         ],
#     )

#     return response.output_text
    
# @api_view(['POST'])
# def Camera_Input(request):
#     image_input = request.data['image_input']
#     prompt = request.data['prompt']
#     try:
#         max_tokens = request.data['max_tokens']
#     except:
#         max_tokens = 1000

#     image_input = f"data:image/jpeg;base64,{image_input}"

#     return Response({'response': Get_GPT_Response(prompt, [image_input], max_tokens)}, status=HTTP_200_OK)

# @api_view(['POST'])
# def Homework_Input(request):
#     user_id = request.data['user_id']
#     mission_id = request.data['mission_id']
#     prompt = request.data['prompt']
#     image_urls = request.data['image_urls']

#     child = models.Children_Accounts.objects.filter(user_id=user_id).first()

#     current_mission = next((mission for mission in child.notification['missions'] if mission['id'] == mission_id), None)
    
#     # If the mission already has a GPT response, return it without calling the API again
#     if current_mission and 'gpt_response' in current_mission and current_mission['gpt_response'] is not None:
#         return Response({'response': current_mission['gpt_response']}, status=HTTP_200_OK)
#     else:
#         try:
#             max_tokens = request.data['max_tokens']
#         except:
#             max_tokens = 1000

#         if image_urls is None:
#             image_urls = []
#         else:
#             image_urls = json.loads(image_urls)

#         # Using the Get_GPT_Response function defined above
#         gpt_response = Get_GPT_Response(prompt, image_urls, max_tokens)

#         # Store the response in the mission to avoid repeated API calls
#         if current_mission:
#             current_mission['gpt_response'] = gpt_response
#             child.save()

#         return Response({'response': gpt_response}, status=HTTP_200_OK)

# FCM Notification Views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from companion_app.models import DeviceToken
from apis.serializers import DeviceTokenSerializer
from apis.firebase_admin import send_push_notification, send_multicast_notification, subscribe_to_topic, unsubscribe_from_topic, send_topic_notification

@api_view(['POST'])
@permission_classes([AllowAny])
def register_device(request):
    """
    Register device token for FCM notifications
    """
    serializer = DeviceTokenSerializer(data=request.data)
    if serializer.is_valid():
        user_id = serializer.validated_data['user_id']
        device_token = serializer.validated_data['device_token']
        device_type = serializer.validated_data.get('device_type', 'android')
        
        # Check if the token already exists for this user
        existing_token = DeviceToken.objects.filter(user_id=user_id, device_token=device_token).first()
        if existing_token:
            # Update existing token if it exists
            existing_token.device_type = device_type
            existing_token.is_active = True
            existing_token.save()
            return Response({
                'status': 'success',
                'message': 'Device token updated successfully',
                'data': DeviceTokenSerializer(existing_token).data
            }, status=status.HTTP_200_OK)
        
        # Create new token
        token_obj = serializer.save()
        return Response({
            'status': 'success',
            'message': 'Device token registered successfully',
            'data': DeviceTokenSerializer(token_obj).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 'error',
        'message': 'Invalid data',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def unregister_device(request):
    """
    Unregister device token
    """
    user_id = request.data.get('user_id')
    device_token = request.data.get('device_token')
    
    if not user_id or not device_token:
        return Response({
            'status': 'error',
            'message': 'user_id and device_token are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token_obj = DeviceToken.objects.get(user_id=user_id, device_token=device_token)
        token_obj.is_active = False
        token_obj.save()
        return Response({
            'status': 'success',
            'message': 'Device token unregistered successfully'
        }, status=status.HTTP_200_OK)
    except DeviceToken.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Device token not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_notification(request):
    """
    Send notification to a specific user
    """
    user_id = request.data.get('user_id')
    title = request.data.get('title')
    body = request.data.get('body')
    data = request.data.get('data', {})
    
    if not user_id or not title or not body:
        return Response({
            'status': 'error',
            'message': 'user_id, title, and body are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get all active device tokens for the user
    tokens = DeviceToken.objects.filter(user_id=user_id, is_active=True).values_list('device_token', flat=True)
    
    if not tokens:
        return Response({
            'status': 'error',
            'message': 'No active device tokens found for this user'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Convert tokens to a list
    tokens_list = list(tokens)
    
    # Send notifications
    if len(tokens_list) == 1:
        result = send_push_notification(tokens_list[0], title, body, data)
    else:
        result = send_multicast_notification(tokens_list, title, body, data)
    
    if result.get('success'):
        return Response({
            'status': 'success',
            'message': 'Notification sent successfully',
            'data': result
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'error',
            'message': 'Failed to send notification',
            'error': result.get('error')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def subscribe_device_to_topic(request):
    """
    Subscribe device tokens to a specific topic
    """
    topic = request.data.get('topic')
    user_id = request.data.get('user_id')
    device_tokens = request.data.get('device_tokens')
    
    if not topic:
        return Response({
            'status': 'error',
            'message': 'topic is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate topic name (FCM has restrictions on topic names)
    if not topic.isalnum() and not all(c in '-_.~%+' for c in topic if not c.isalnum()):
        return Response({
            'status': 'error',
            'message': 'Invalid topic name. Use only letters, numbers, and -_.~%+'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    tokens_list = []
    
    # If user_id is provided, get all tokens for that user
    if user_id:
        tokens = DeviceToken.objects.filter(user_id=user_id, is_active=True).values_list('device_token', flat=True)
        tokens_list.extend(list(tokens))
    
    # If specific device_tokens are provided, add them too
    if device_tokens and isinstance(device_tokens, list):
        tokens_list.extend(device_tokens)
    
    # Remove duplicates
    tokens_list = list(set(tokens_list))
    
    if not tokens_list:
        return Response({
            'status': 'error',
            'message': 'No device tokens found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Subscribe tokens to topic
    result = subscribe_to_topic(tokens_list, topic)
    
    if result.get('success'):
        return Response({
            'status': 'success',
            'message': f'Devices subscribed to topic {topic} successfully',
            'data': result
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'error',
            'message': 'Failed to subscribe devices to topic',
            'error': result.get('error')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def unsubscribe_device_from_topic(request):
    """
    Unsubscribe device tokens from a specific topic
    """
    topic = request.data.get('topic')
    user_id = request.data.get('user_id')
    device_tokens = request.data.get('device_tokens')
    
    if not topic:
        return Response({
            'status': 'error',
            'message': 'topic is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    tokens_list = []
    
    # If user_id is provided, get all tokens for that user
    if user_id:
        tokens = DeviceToken.objects.filter(user_id=user_id, is_active=True).values_list('device_token', flat=True)
        tokens_list.extend(list(tokens))
    
    # If specific device_tokens are provided, add them too
    if device_tokens and isinstance(device_tokens, list):
        tokens_list.extend(device_tokens)
    
    # Remove duplicates
    tokens_list = list(set(tokens_list))
    
    if not tokens_list:
        return Response({
            'status': 'error',
            'message': 'No device tokens found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Unsubscribe tokens from topic
    result = unsubscribe_from_topic(tokens_list, topic)
    
    if result.get('success'):
        return Response({
            'status': 'success',
            'message': f'Devices unsubscribed from topic {topic} successfully',
            'data': result
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'error',
            'message': 'Failed to unsubscribe devices from topic',
            'error': result.get('error')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_topic_message(request):
    """
    Send notification to all devices subscribed to a specific topic
    """
    topic = request.data.get('topic')
    title = request.data.get('title')
    body = request.data.get('body')
    data = request.data.get('data', {})
    
    if not topic or not title or not body:
        return Response({
            'status': 'error',
            'message': 'topic, title, and body are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Send notification to topic
    result = send_topic_notification(topic, title, body, data)
    
    if result.get('success'):
        return Response({
            'status': 'success',
            'message': f'Notification sent to topic {topic} successfully',
            'data': result
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'status': 'error',
            'message': 'Failed to send notification to topic',
            'error': result.get('error')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)