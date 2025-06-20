from django.shortcuts import render
from companion_app import models
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from rest_framework.decorators import api_view
from apis.firebase_admin import send_multicast_notification, send_push_notification, send_topic_notification
from apis.scheduler import schedule_mission_reminder
from companion_app.models import DeviceToken
import random
import string
import json
import uuid
import datetime
from django.utils import timezone
import pytz
from google.cloud import storage
from google.oauth2 import service_account
import os

# Set the Jakarta timezone
JAKARTA_TZ = pytz.timezone('Asia/Jakarta')

# Initialize Firebase Storage
creds_dict = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
credentials = service_account.Credentials.from_service_account_info(creds_dict)
client = storage.Client(credentials=credentials)
bucket = client.bucket(os.getenv("FIREBASE_BUCKET"))

class MissionViews:
    @staticmethod
    @api_view(['POST'])
    def mission_add(request):
        user_id = request.data['user_id']
        mission_type = request.data['mission_type']
        mission_title = request.data['mission_title']
        mission_due_date = request.data['mission_due_date']
        mission_due_time = request.data['mission_due_time']
        mission_repeat = request.data['mission_repeat']
            
        mission_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        mission_data = {
            'id': mission_id,
            'title': mission_title,
            'due_date': mission_due_date,
            'due_time': mission_due_time,
            'category': mission_type,
            'completed': False,
            'repeat': mission_repeat,
            'gpt_response': None,
        }
        
        if mission_type == 'Homework':
            mission_data['instructions'] = request.data['mission_instructions']
            mission_data['confirmation'] = False
            mission_data['claimable'] = False
            
            # Handle all file attachments from request.FILES
            if request.FILES:
                attachment_urls = []
                
                # Process each file in request.FILES
                for file_key, attachment_file in request.FILES.items():
                    # Generate a unique file name
                    file_extension = attachment_file.name.split('.')[-1]
                    unique_filename = f"mission_attachments/{user_id}/{str(uuid.uuid4())}.{file_extension}"
                    
                    # Upload to Firebase storage
                    blob = bucket.blob(unique_filename)
                    blob.upload_from_file(
                        attachment_file.file,
                        content_type=attachment_file.content_type
                    )
                    
                    # Get the download URL
                    blob.make_public()
                    attachment_url = blob.public_url
                    
                    # Add the URL to the list
                    attachment_urls.append(attachment_url)
                
                # Add all URLs to the mission data
                mission_data['attachments'] = attachment_urls

        # Get the child and add the mission
        child = models.Children_Accounts.objects.filter(user_id=user_id).first()
        child.notification['missions'].append(mission_data)
        child.save()

        # Send immediate notification
        # send_topic_notification(
        #     topic=user_id,
        #     title="You got new mission!",
        #     body=f"A new mission '{mission_title}' has been assigned",
        # )
        
        # Schedule a reminder notification for the due date/time
        try:
            # Parse the due date and time
            due_date_parts = mission_due_date.split('-')
            due_time_parts = mission_due_time.split(':')
            
            if len(due_date_parts) == 3 and len(due_time_parts) >= 2:
                year, month, day = map(int, due_date_parts)
                hour, minute = map(int, due_time_parts[:2])
                
                # Create a datetime object for the due date/time
                due_datetime = datetime.datetime(year, month, day, hour, minute)
                
                # Make it timezone-aware with Jakarta timezone
                due_datetime = JAKARTA_TZ.localize(due_datetime)
                
                # Get current time in Jakarta timezone
                now = timezone.now().astimezone(JAKARTA_TZ)
                
                # If the due time is in the future, schedule a reminder
                if due_datetime > now:
                    # Schedule a reminder 1 hour before the due time
                    delta_time = due_datetime - now

                    print("REMINDER TIME: ", delta_time)
                    print("TIMEZONE NOW: ", now)
                    
                    # Only schedule if the reminder time is still in the future
                    # if delta_time < datetime.timedelta(minutes=10):
                        # Use the scheduler function directly (not as a Celery task)
                    schedule_mission_reminder(
                        user_id=user_id,
                        mission_id=mission_id,
                        reminder_time=due_datetime,
                        category="mission"
                    )
        except Exception as e:
            # If there's an error scheduling the reminder, just log it and continue
            print(f"Error scheduling reminder: {e}")
        
        return Response({'message': 'Mission added successfully'}, status=HTTP_201_CREATED)
    
    @staticmethod
    @api_view(['GET'])
    def mission_get(request):
        user_id = request.GET.get('user_id')
        child = models.Children_Accounts.objects.filter(user_id=user_id).first()
        missions = child.notification['missions']

        return Response({'missions': missions}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def mission_update(request):
        user_id = request.data['user_id']
        mission_id = request.data['mission_id']
        mission_type = request.data['mission_type']
        mission_title = request.data['mission_title']
        mission_due_date = request.data['mission_due_date']
        mission_due_time = request.data['mission_due_time']
        mission_repeat = request.data['mission_repeat'] 

        try:
            mission_attachments_urls = json.loads(request.data.get('attachment_urls', '[]'))
        except:
            mission_attachments_urls = None
        
        if mission_type == 'Homework':
            mission_instructions = request.data['mission_instructions']
        
        child = models.Children_Accounts.objects.filter(user_id=user_id).first()
        
        # Find the mission and delete any attachments from Firebase
        missions = child.notification['missions']
        existing_attachments = []
        
        for i, mission in enumerate(missions):
            if mission['id'] == mission_id:
                # Save existing attachments that weren't deleted
                if 'attachments' in mission and mission['attachments']:
                    for attachment_url in mission['attachments']:
                        if mission_attachments_urls and attachment_url in mission_attachments_urls:
                            existing_attachments.append(attachment_url)
                            continue
                        # Extract the file path from the URL and delete from storage
                        try:
                            # Extract the storage path from URL
                            if 'https://storage.googleapis.com/companion-app-1b431.firebasestorage.app/' in attachment_url:
                                storage_path = attachment_url.replace('https://storage.googleapis.com/companion-app-1b431.firebasestorage.app/', '')
                                blob = bucket.blob(storage_path)
                                blob.delete()
                        except Exception as e:
                            print(f"Error deleting file from Firebase: {e}")
                
                # Remove the mission from the list
                del missions[i]
                break
        
        # Create a new mission with updated data
        new_mission = {
            'id': mission_id,
            'title': mission_title,
            'due_date': mission_due_date,
            'due_time': mission_due_time,
            'repeat': mission_repeat,
            'category': mission_type,
            'completed': False,
        }
        
        if mission_type == 'Homework':
            new_mission['instructions'] = mission_instructions
            new_mission['confirmation'] = False
            new_mission['gpt_response'] = None
            new_mission['claimable'] = False
            
            # Handle all file attachments from request.FILES
            if request.FILES:
                attachment_urls = existing_attachments
                
                # Process each file in request.FILES
                for file_key, attachment_file in request.FILES.items():
                    # Generate a unique file name
                    file_extension = attachment_file.name.split('.')[-1]
                    unique_filename = f"mission_attachments/{user_id}/{str(uuid.uuid4())}.{file_extension}"
                    
                    # Upload to Firebase storage
                    blob = bucket.blob(unique_filename)
                    blob.upload_from_file(
                        attachment_file.file,
                        content_type=attachment_file.content_type
                    )
                    
                    # Get the download URL
                    blob.make_public()
                    attachment_url = blob.public_url
                    
                    # Add the URL to the list
                    attachment_urls.append(attachment_url)
                
                # Add all URLs to the mission data
                new_mission['attachments'] = attachment_urls
            elif existing_attachments:
                # Keep existing attachments that weren't deleted
                new_mission['attachments'] = existing_attachments
        
        # Add the new mission back to the list
        child.notification['missions'].append(new_mission)
        child.save()

        return Response({'message': 'Mission updated successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['DELETE'])
    def mission_delete(request):
        user_id = request.data['user_id']
        mission_id = request.data['mission_id']

        child = models.Children_Accounts.objects.filter(user_id=user_id).first()
        child.notification['missions'] = [mission for mission in child.notification['missions'] if mission['id'] != mission_id]
        child.save()

        return Response({'message': 'Mission deleted successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def mission_complete(request):
        try:
            user_id = request.data['user_id']
            mission_id = request.data['mission_id']

            child = models.Children_Accounts.objects.filter(user_id=user_id).first()
            for mission in child.notification['missions']:
                if mission['id'] == mission_id:
                    mission['completed'] = True

                    if mission['category'] == 'Homework':
                        mission['confirmation'] = False
                        mission['gpt_response'] = None
                        mission['claimable'] = True
                    break
            child.save()
            
            if mission['category'] == 'Homework':
                send_topic_notification(
                    topic=user_id,
                    title="Mission completed!",
                    body=f"Parents has confirmed your mission, go claim your reward!",
                )
        except:
            user_id = request.data['message']['toolCalls'][0]['function']['arguments']['user_id']
            mission_id = request.data['message']['toolCalls'][0]['function']['arguments']['mission_id']

            child = models.Children_Accounts.objects.filter(user_id=user_id).first()
            for mission in child.notification['missions']:
                if mission['id'] == mission_id:
                    mission['confirmation'] = True
                    break
            child.save()
        
        return Response({'message': 'Mission completed successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['GET'])
    def mission_check_completion(request):
        user_id = request.GET.get('user_id')
        mission_id = request.GET.get('mission_id')

        child = models.Children_Accounts.objects.filter(user_id=user_id).first()

        current_mission = next((mission for mission in child.notification['missions'] if mission['id'] == mission_id), None)



        if current_mission['confirmation'] == True:
            return Response({'status': 'Completed'}, status=HTTP_200_OK)
        else:
            return Response({'status': 'Not Completed'}, status=HTTP_200_OK)
        
    @staticmethod
    @api_view(['POST'])
    def mission_claim(request):
        user_id = request.data['user_id']
        mission_id = request.data['mission_id']
        
        child = models.Children_Accounts.objects.filter(user_id=user_id).first()
        for mission in child.notification['missions']:
            if mission['id'] == mission_id:
                mission['claimable'] = False
                break
        child.save()
        
        return Response({'message': 'Mission claimed successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def mission_add_result(request):
        user_id = request.data['user_id']
        mission_id = request.data['mission_id']

        child = models.Children_Accounts.objects.filter(user_id=user_id).first()
        mission = next((mission for mission in child.notification['missions'] if mission['id'] == mission_id), None)

        # Handle all file attachments from request.FILES
        if request.FILES:
            result_urls = []
            
            # Process each file in request.FILES
            for file_key, attachment_file in request.FILES.items():
                # Generate a unique file name
                file_extension = attachment_file.name.split('.')[-1]
                unique_filename = f"mission_attachments/{user_id}/{str(uuid.uuid4())}.{file_extension}"
                
                # Upload to Firebase storage
                blob = bucket.blob(unique_filename)
                blob.upload_from_file(
                    attachment_file.file,
                    content_type=attachment_file.content_type
                )
                
                # Get the download URL
                blob.make_public()
                result_url = blob.public_url
                
                # Add the URL to the list
                result_urls.append(result_url)
            
            # Add all URLs to the mission data
            mission['results'] = result_urls

        child.save()

        return Response({'message': 'Mission result added successfully'}, status=HTTP_200_OK)

Mission_Add = MissionViews.mission_add
Mission_Get = MissionViews.mission_get
Mission_Update = MissionViews.mission_update
Mission_Delete = MissionViews.mission_delete
Mission_Complete = MissionViews.mission_complete
Mission_Check_Completion = MissionViews.mission_check_completion 
Mission_Add_Result = MissionViews.mission_add_result
Mission_Claim = MissionViews.mission_claim