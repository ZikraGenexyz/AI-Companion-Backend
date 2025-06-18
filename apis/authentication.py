from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
import os

class APIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication class for API key authentication.
    The API key should be included in the request header as:
    Authorization: Api-Key xxxxxxxxxxxxxxxxxxxxxxx
    """
    
    def authenticate(self, request):
        # Get the API key from request header
        api_key_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not api_key_header:
            return None
        
        # Check if the header starts with 'Api-Key '
        if not api_key_header.startswith('Api-Key '):
            return None
            
        # Extract the key
        key = api_key_header.split('Api-Key ')[1].strip()
        
        # Get the valid API key from environment variables
        valid_api_key = os.getenv('API_KEY')
        
        if not valid_api_key:
            # If API_KEY is not set in environment, use a default from settings
            valid_api_key = getattr(settings, 'API_KEY', None)
            
        if not valid_api_key:
            # If still no API key is configured, authentication fails
            raise AuthenticationFailed('API key authentication is not properly configured')
            
        # Check if the provided key matches the valid key
        if key != valid_api_key:
            raise AuthenticationFailed('Invalid API key')
        
        # Authentication successful, return an AnonymousUser
        # This allows permission checks to work with IsAuthenticated
        user = AnonymousUser()
        return (user, key)
    
    def authenticate_header(self, request):
        return 'Api-Key' 