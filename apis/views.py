from django.shortcuts import render
from companion_app import models
from .serializers import UserSerializer, ChatsSerializer
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.views.decorators.csrf import csrf_exempt, csrf_protect

# Create your views here.
class ListUser(generics.ListCreateAPIView):
    queryset = models.User_Data.objects.all()
    serializer_class = UserSerializer

class HistoryChat(generics.ListCreateAPIView):
    queryset = models.Chat_History.objects.all()
    serializer_class = ChatsSerializer

@csrf_protect
def Login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)

        if user is not None:    
            return Response({'message': 'Login successful'}, status=HTTP_200_OK)
        else:
            return Response({'message': 'Invalid credentials'}, status=HTTP_400_BAD_REQUEST)
        
    return Response({'message': 'Invalid request method'}, status=HTTP_400_BAD_REQUEST)
