from django.shortcuts import render
from companion_app import models
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view
from ..serializers import ChatsSerializer
from rest_framework import generics
from companion_app import models

class HistoryChat(generics.ListCreateAPIView):
    queryset = models.Chat_History.objects.all()
    serializer_class = ChatsSerializer
    
class ChatViews:
    @staticmethod
    @api_view(['DELETE'])
    def reset_chat(request):
        models.Chat_History.objects.filter(user_id=request.data['user_id']).delete()
        return Response({'message': 'Chat reset successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def get_chat(request):
        chat = models.Chat_History.objects.filter(user_id=request.data['user_id'], isUser=True)
        summary = ''
        for c in chat:
            summary += c.text + ', '
        
        summary += '[do not respond]'

        return Response({'summary': summary}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['PUT'])
    def add_chat(request):
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

# Legacy function-based views for backward compatibility
ResetChat = ChatViews.reset_chat
GetChat = ChatViews.get_chat
AddChat = ChatViews.add_chat 