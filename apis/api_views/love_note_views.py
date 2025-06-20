from django.shortcuts import render
from companion_app import models
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.decorators import api_view
import random
import string
import json
import uuid
from google.cloud import storage
from google.oauth2 import service_account
import os

# Initialize Firebase Storage
creds_dict = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
credentials = service_account.Credentials.from_service_account_info(creds_dict)
client = storage.Client(credentials=credentials)
bucket = client.bucket(os.getenv("FIREBASE_BUCKET"))

class LoveNoteViews:
    @staticmethod
    @api_view(['PUT'])
    def love_note_add(request):
        user_id = request.data['user_id']
        love_note = request.data['love_note']

        child = models.Children_Accounts.objects.filter(user_id=user_id).first()
        child.notification['love_notes'].append({
            'note': love_note,
            'completed': False
        })
        child.save()

        return Response({'message': 'Love note added successfully'}, status=HTTP_200_OK)
    
    @staticmethod
    @api_view(['POST'])
    def love_note_count(request):
        user_id = request.data['message']['toolCalls'][0]['function']['arguments']['user_id']

        child = models.Children_Accounts.objects.filter(user_id=user_id).first()

        love_notes = child.notification['love_notes']

        uncompleted_love_notes = [note for note in love_notes if not note['completed']]
        
        return Response({"results":[{"result": f'There is {len(uncompleted_love_notes)} love notes.', "toolCallId": request.data['message']['toolCalls'][0]['id']}]}, status=HTTP_200_OK)
        
    @staticmethod
    @api_view(['POST'])
    def love_note_get(request):
        try:
            user_id = request.data['user_id']
            getUncompleted = True if request.data['get_uncompleted'] == 'true' else False
        except:
            user_id = request.data['message']['toolCalls'][0]['function']['arguments']['user_id']
            getUncompleted = True

        child = models.Children_Accounts.objects.filter(user_id=user_id).first()
        love_notes = child.notification['love_notes']
        uncompleted_love_notes = [note for note in child.notification['love_notes'] if not note['completed']]

        if getUncompleted:
            notes = f'There is {len(uncompleted_love_notes)} love notes for you. \n'
            
            # First build the response with uncompleted notes
            for note in uncompleted_love_notes:
                notes += f"{note['note']}, \n"
            
            # Then mark all uncompleted notes as completed
            for i, note in enumerate(child.notification['love_notes']):
                if not note['completed']:
                    child.notification['love_notes'][i]['completed'] = True
            
            child.save()
                
            notes = notes.rstrip(', \n')
            return Response({"results":[{"result": notes, "toolCallId": request.data['message']['toolCalls'][0]['id']}]}, status=HTTP_200_OK)
        else:
            return Response({'love_notes': love_notes}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['PUT'])
    def love_note_update(request):
        user_id = request.data['user_id']
        index = int(request.data['index'])
        love_note = request.data['love_note']

        child = models.Children_Accounts.objects.filter(user_id=user_id).first()
        child.notification['love_notes'][index]['note'] = love_note
        child.save()

        return Response({'message': 'Love note updated successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['DELETE'])
    def love_note_delete(request):
        user_id = request.data['user_id']
        index = int(request.data['index'])

        child = models.Children_Accounts.objects.filter(user_id=user_id).first()
        child.notification['love_notes'].pop(index)
        child.save()

        return Response({'message': 'Love note removed successfully'}, status=HTTP_200_OK)

# Legacy function-based views for backward compatibility
Love_Note_Add = LoveNoteViews.love_note_add
Love_Note_Get = LoveNoteViews.love_note_get
Love_Note_Update = LoveNoteViews.love_note_update
Love_Note_Delete = LoveNoteViews.love_note_delete
Love_Note_Count = LoveNoteViews.love_note_count