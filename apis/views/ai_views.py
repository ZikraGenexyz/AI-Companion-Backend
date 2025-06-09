from django.shortcuts import render
from companion_app import models
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view
import os
from dotenv import load_dotenv
import json
import requests
from serpapi import GoogleSearch
from openai import OpenAI
import base64

# Load environment variables
load_dotenv()

class AIViews:
    @staticmethod
    @api_view(['POST'])
    def google_search_api(request):
        search = GoogleSearch({
            "q": request.data['query'], 
            "location": "Indonesia, Jakarta",
            "api_key": os.getenv('GOOGLE_API_KEY')
        })

        result = search.get_dict()
        result = result['search_results']['related_questions'][0]['snippet']

        return Response({'search_results': result}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def generate_image(request):
        engine_id = "stable-diffusion-v1-6"
        api_host = os.getenv('API_HOST', 'https://api.stability.ai')
        api_key = os.getenv('STABILITY_API_KEY')

        if api_key is None:
            raise Exception("Missing Stability API key.")

        response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "text_prompts": [
                    {
                        "text": request.data['prompt']
                    }
                ],
                "cfg_scale": 7,
                "height": 1024,
                "width": 576,
                "samples": 1,
                "steps": 30,
            },
        )

        if response.status_code == 200:
            data = response.json()
            image_data = data['artifacts'][0]['base64']
            
            return Response({
                'success': True,
                'image': image_data,
            }, status=HTTP_200_OK)
        else:
            return Response({
                'success': False, 
                'error': response.json()
            }, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    @api_view(['GET'])
    def get_assistant_id(request):
        nekokuma = os.getenv('NEKOKUMA_ID')
        return Response({'nekokuma': nekokuma}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def camera_input(request):
        image_input = request.data['image_input']
        prompt = request.data['prompt']
        try:
            max_tokens = request.data['max_tokens']
        except:
            max_tokens = 1000

        image_input = f"data:image/jpeg;base64,{image_input}"
        
        # Get response from GPT
        response = AIViews._get_gpt_response(prompt, [image_input], max_tokens)
        return Response({'response': response}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def homework_input(request):
        user_id = request.data['user_id']
        mission_id = request.data['mission_id']
        prompt = request.data['prompt']
        image_urls = request.data['image_urls']

        child = models.Children_Accounts.objects.filter(user_id=user_id).first()

        current_mission = next((mission for mission in child.notification['missions'] if mission['id'] == mission_id), None)
        
        # If the mission already has a GPT response, return it without calling the API again
        if current_mission and 'gpt_response' in current_mission and current_mission['gpt_response'] is not None:
            return Response({'response': current_mission['gpt_response']}, status=HTTP_200_OK)
        else:
            try:
                max_tokens = request.data['max_tokens']
            except:
                max_tokens = 1000

            if image_urls is None:
                image_urls = []
            else:
                image_urls = json.loads(image_urls)

            # Using the _get_gpt_response method
            gpt_response = AIViews._get_gpt_response(prompt, image_urls, max_tokens)

            # Store the response in the mission to avoid repeated API calls
            if current_mission:
                current_mission['gpt_response'] = gpt_response
                child.save()

            return Response({'response': gpt_response}, status=HTTP_200_OK)

    @staticmethod
    def _get_gpt_response(prompt, image_urls, max_tokens):
        """Helper method to get response from GPT model with image inputs"""
        # Build content array starting with text
        api_key = os.getenv('OPENAI_API_KEY')
        client = OpenAI(api_key=api_key)
        content = [
            {"type": "input_text", "text": prompt},
        ]

        # Add each image URL or base64 to the content array
        for image_url in image_urls:
            content.append({"type": "input_image", "image_url": f"{image_url}"})

        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
        )

        return response.output_text


# Legacy function-based views for backward compatibility
GoogleSearchApi = AIViews.google_search_api
GenerateImage = AIViews.generate_image
Get_Assistant_ID = AIViews.get_assistant_id
Camera_Input = AIViews.camera_input
Homework_Input = AIViews.homework_input 