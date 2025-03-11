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

logger = logging.getLogger(__name__)

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
def Login(request):
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
    # if request.method == 'POST':
    user = User.objects.create_user(request.data['username'], request.data['email'], request.data['password'])
    user.save()
    return Response({'message': 'Account created successfully'}, status=HTTP_201_CREATED)
    # return Response({'message': 'Invalid request method'}, status=HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def ResetChat(request):
    user = User.objects.get(username=request.data['user'])
    models.Chat_History.objects.filter(user=user).delete()
    return Response({'message': 'Chat reset successfully'}, status=HTTP_200_OK)
    # return Response({'message': 'Invalid request method'}, status=HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def GetChat(request):
    user = User.objects.get(username=request.data['user'])
    chat = models.Chat_History.objects.filter(user=user)
    serializer = ChatsSerializer(chat, many=True)
    return Response(serializer.data, status=HTTP_200_OK)

@api_view(['POST'])
def AddChat(request):
    # Get the text from the request
    text = request.data['text']
    # use_cartesia = request.data['useCartesia']
    use_cartesia = False

    user = User.objects.get(username=request.data['user'])

    conversation_history = models.Chat_History.objects.filter(user=user)
    conversation_history = ChatsSerializer(conversation_history, many=True).data
    conversation_history = [item['text'] for item in conversation_history]

    if not text:
        return JsonResponse({'error': 'No text provided'}, status=400)
    
    # Prepare messages for Groq
    messages = [
        {
            "role": "system",
            "content": """You are a Robot, a friendly and enthusiastic robot companion with a playful personality. 
            You love helping people. Your responses should be:
            - Warm and friendly
            - Keep responses concise but engaging
            - Show genuine interest in the user
            - Use a casual, conversational tone
            - Sometimes add playful remarks or gentle humor
            - Always maintain a positive and encouraging attitude
            - Reference previous parts of the conversation when relevant
            - Maintain context from earlier exchanges
            - respond with a shorter response
            
            Example responses:
            "Hey there! I'd love to help you with that!"
            "That's a great question! Let me think about it..."
            "Awesome! I'm excited to help you with this!"
            """
        }
    ]

    # Add conversation history
    messages.extend(conversation_history)
    
    # Add current user message
    messages.append({
        "role": "user",
        "content": text
    })

    # Generate AI response using Groq
    logger.debug("Generating AI response with Groq")
    chat_completion = groq_client.chat.completions.create(
        messages=messages,
        model="llama-3.2-3b-preview",
        temperature=0.7,
        max_tokens=1000,
    )
        
    ai_response = chat_completion.choices[0].message.content
    ai_response = ai_response.split("</think>")[-1]

    if use_cartesia:
        # Convert AI response to speech using Cartesia
        logger.debug("Converting response to speech with Cartesia")
        output_format = {
            "container": "mp3",
            "encoding": "mp3",
            "sample_rate": 44100,
            "bit_rate": 128000
        }

        # Add natural pauses with punctuation
        speech_response = ai_response
        speech_response = speech_response.replace('!', '! ')
        speech_response = speech_response.replace('?', '? ')
        speech_response = speech_response.replace('.', '. ')
        speech_response = ' '.join(speech_response.split('*')[::2])
    
        # Generate speech using Cartesia with cheerful voice
        audio_data = cartesia_client.tts.bytes(
            model_id="sonic-english",
            transcript=speech_response,
            voice_id="694f9389-aac1-45b6-b726-9d9369183238",
            output_format=output_format
        )
    
        # Convert audio data directly to base64 without saving to file
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    else:
        audio_base64 = None

    models.Chat_History.objects.create(text=text, user=user, isUser=True)
    models.Chat_History.objects.create(text=ai_response, user=user, isUser=False)
    
    return JsonResponse({
        'success': True,
        'response': ai_response,
        'audio': audio_base64
    }, status=HTTP_200_OK)

    return Response({'message': 'Chat reset successfully'}, status=HTTP_200_OK)
    # return Response({'message': 'Invalid request method'}, status=HTTP_400_BAD_REQUEST)
