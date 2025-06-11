import firebase_admin
from firebase_admin import credentials, messaging
import os
from pathlib import Path
from django.conf import settings

# Initialize Firebase Admin with service account key
cred_path = os.path.join(settings.BASE_DIR, 'companion-app-1b431-firebase-adminsdk-fbsvc-885c1c1f19.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def send_push_notification(token, title, body, data=None):
    """
    Send push notification to a specific device token
    
    Args:
        token (str): FCM device token
        title (str): Notification title
        body (str): Notification body
        data (dict, optional): Additional data to send. Defaults to None.
    
    Returns:
        dict: Response from FCM
    """
    try:
        # Create message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
        )
        
        # Send message
        response = messaging.send(message)
        return {
            "success": True,
            "message_id": response
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def send_multicast_notification(tokens, title, body, data=None):
    """
    Send push notification to multiple device tokens
    
    Args:
        tokens (list): List of FCM device tokens
        title (str): Notification title
        body (str): Notification body
        data (dict, optional): Additional data to send. Defaults to None.
    
    Returns:
        dict: Response from FCM
    """
    try:
        # Create multicast message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=tokens,
        )
        
        # Send multicast message
        response = messaging.send_multicast(message)
        return {
            "success": True,
            "success_count": response.success_count,
            "failure_count": response.failure_count,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }