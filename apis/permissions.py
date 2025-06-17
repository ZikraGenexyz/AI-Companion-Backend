from rest_framework.permissions import BasePermission

class HasAPIKey(BasePermission):
    """
    Custom permission to allow requests authenticated with API key.
    """
    
    def has_permission(self, request, view):
        # If the request was authenticated with our APIKeyAuthentication,
        # the auth credentials will be the API key
        return request.auth is not None 