from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
from datetime import datetime
import groq
from dotenv import load_dotenv
import base64
import logging
import traceback
import webrtcvad
from cartesia import Cartesia

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize VAD
vad = webrtcvad.Vad()
vad.set_mode(1)  # Set aggressiveness mode (0-3)

# Initialize Groq client
groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))

# Initialize Cartesia client
cartesia_client = Cartesia(api_key=os.getenv('CARTESIA_API_KEY'))

# Create your views here.
def myapp(request):
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def process_audio(request):
    try:
        logger.debug("Starting text processing")
        # Get the text from the request
        data = json.loads(request.body)
        text = data.get('text')
        
        if not text:
            logger.error("No text provided in request")
            return JsonResponse({'error': 'No text provided'}, status=400)

        try:
            # Generate AI response using Groq
            logger.debug("Generating AI response with Groq")
            chat_completion = groq_client.chat.completions.create(
                messages=[
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
                        
                        Example responses:
                        "Hey there! I'd love to help you with that!"
                        "That's a great question! Let me think about it..."
                        "Awesome! I'm excited to help you with this!"
                        """
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=1000,
            )
            
            ai_response = chat_completion.choices[0].message.content
            logger.debug(f"AI response generated: {ai_response}")
            
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
            
            # Generate speech using Cartesia with cheerful voice
            audio_data = cartesia_client.tts.bytes(
                model_id="sonic-english",
                transcript=speech_response,
                voice_id="694f9389-aac1-45b6-b726-9d9369183238",
                output_format=output_format
            )
            
            # Convert audio data directly to base64 without saving to file
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            logger.debug("Processing completed successfully")
            
            return JsonResponse({
                'success': True,
                'response': ai_response,
                'audio': audio_base64
            })
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            logger.error(traceback.format_exc())
            return JsonResponse({
                'error': f'Error processing text: {str(e)}'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'error': f'An error occurred: {str(e)}'
        }, status=500)