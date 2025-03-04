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
from cartesia import Cartesia

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure audio file storage
AUDIO_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
logger.debug(f"Audio storage directory: {AUDIO_STORAGE_DIR}")
os.makedirs(AUDIO_STORAGE_DIR, exist_ok=True)

# Initialize Groq client
groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))

# Initialize Cartesia client
cartesia_client = Cartesia(api_key=os.getenv('CARTESIA_API_KEY'))

def get_audio_file_paths():
    """
    Generate unique file paths for audio files.
    
    Returns:
        tuple: (input_wav_path, response_mp3_path)
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response_mp3_path = os.path.join(AUDIO_STORAGE_DIR, f"response_{timestamp}.mp3")
    return response_mp3_path

# Create your views here.
def myapp(request):
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def process_audio(request):
    response_mp3_path = None
    try:
        logger.debug("Starting text processing")
        # Get the text from the request
        data = json.loads(request.body)
        text = data.get('text')
        
        if not text:
            logger.error("No text provided in request")
            return JsonResponse({'error': 'No text provided'}, status=400)

        # Get file path for response audio
        response_mp3_path = get_audio_file_paths()
        logger.debug(f"Response MP3 path: {response_mp3_path}")

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
            
            # Save the audio data
            logger.debug("Saving response audio")
            try:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(response_mp3_path), exist_ok=True)
                logger.debug(f"Directory created/verified: {os.path.dirname(response_mp3_path)}")
                
                # Save the file
                with open(response_mp3_path, 'wb') as f:
                    f.write(audio_data)
                logger.debug(f"Response audio saved to: {response_mp3_path}")
                
                # Verify the file exists
                if not os.path.exists(response_mp3_path):
                    raise FileNotFoundError(f"Failed to create audio file at {response_mp3_path}")
                
                # Read the audio file and convert to base64
                logger.debug("Converting response audio to base64")
                with open(response_mp3_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                logger.debug("Processing completed successfully")
                
                # Delete the audio file after sending
                try:
                    os.remove(response_mp3_path)
                    logger.debug(f"Deleted audio file: {response_mp3_path}")
                except Exception as e:
                    logger.error(f"Error deleting audio file: {str(e)}")
                
                return JsonResponse({
                    'success': True,
                    'response': ai_response,
                    'audio': audio_base64
                })
            except Exception as e:
                logger.error(f"Error saving/reading audio file: {str(e)}")
                logger.error(traceback.format_exc())
                return JsonResponse({
                    'error': f'Error processing audio file: {str(e)}'
                }, status=500)
            
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