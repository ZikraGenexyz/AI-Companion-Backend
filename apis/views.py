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
# Create your views here.
class HistoryChat(generics.ListCreateAPIView):
    queryset = models.Chat_History.objects.all()
    serializer_class = ChatsSerializer

@api_view(['POST'])
def Login(request):
    if request.method == 'POST':
        auth_data = request.data
        if '@' in auth_data['username']:
            user = User.objects.get(email=auth_data['username'])
            
            if user.check_password(auth_data['password']):
                return Response({'message': 'Login successful'}, status=HTTP_200_OK)
            else:
                return Response({'message': 'Invalid credentials'}, status=HTTP_400_BAD_REQUEST)

        else:
            user = authenticate(username=auth_data['username'], password=auth_data['password'])

            if user is None:
                return Response({'message': 'Invalid credentials'}, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Login successful'}, status=HTTP_200_OK)

@api_view(['POST'])
def CreateAccount(request):
    if request.method == 'POST':
        user = User.objects.create_user(request.data['username'], request.data['email'], request.data['password'])
        user.save()
        return Response({'message': 'Account created successfully'}, status=HTTP_201_CREATED)
    return Response({'message': 'Invalid request method'}, status=HTTP_400_BAD_REQUEST)

def AddChat(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.data['user'])
        chat = models.Chat_History.objects.create(text=request.data['text'], user=user, isUser=True)
        chat.save()
        return Response({'message': 'Chat added successfully'}, status=HTTP_201_CREATED)
    return Response({'message': 'Invalid request method'}, status=HTTP_400_BAD_REQUEST)
