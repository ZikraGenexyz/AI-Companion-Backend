from django.shortcuts import render
from companion_app import models
from .serializers import UserSerializer, ChatsSerializer, LoginSerializer
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
# Create your views here.
class ListUser(generics.ListCreateAPIView):
    queryset = models.User_Data.objects.all()
    serializer_class = UserSerializer

class HistoryChat(generics.ListCreateAPIView):
    queryset = models.Chat_History.objects.all()
    serializer_class = ChatsSerializer

@api_view(['POST'])
def Login(request):
    if request.method == 'POST':
        auth_data = request.data
        user = authenticate(username=auth_data['username'], password=auth_data['password'])
        if user is None:
            return Response({'message': 'Invalid credentials'}, status=HTTP_400_BAD_REQUEST)
        return Response({'message': 'Login successful'}, status=HTTP_200_OK)
    # serializer = LoginSerializer(data=request.data)
    # if serializer.is_valid():
    #     return Response(serializer.data, status=HTTP_200_OK)
    # return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)