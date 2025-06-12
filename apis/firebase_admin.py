import firebase_admin
from firebase_admin import credentials, messaging
import os
import json
import base64
from pathlib import Path
from django.conf import settings

# Function to get Firebase credentials either from file or environment variable
def get_firebase_credentials():
    # First check if FIREBASE_CREDENTIALS env var exists (for Vercel)
    firebase_credentials = os.environ.get('FIREBASE_CREDENTIALS')
    if firebase_credentials:
        try:
            # First attempt to parse it directly as JSON
            try:
                cred_dict = json.loads(firebase_credentials)
                return credentials.Certificate(cred_dict)
            except json.JSONDecodeError:
                # If direct JSON parsing fails, try base64 decoding
                credentials_json = base64.b64decode(firebase_credentials).decode('utf-8')
                return credentials.Certificate(json.loads(credentials_json))
        except Exception as e:
            print(f"Error loading credentials from environment variable: {e}")
    
    # Fallback to file-based credentials (for local development)
    cred_path = os.path.join(settings.BASE_DIR, 'companion-app-1b431-firebase-adminsdk-fbsvc-885c1c1f19.json')
    if os.path.exists(cred_path):
        return credentials.Certificate(cred_path)
    
    # If no credentials are found, raise an error
    raise FileNotFoundError("Firebase credentials not found. Please set FIREBASE_CREDENTIALS environment variable or provide the JSON file.")

# Initialize Firebase Admin with service account
if not firebase_admin._apps:
    cred = get_firebase_credentials()
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

def subscribe_to_topic(tokens, topic):
    """
    Subscribe device tokens to a specific topic
    
    Args:
        tokens (list): List of FCM device tokens
        topic (str): Topic name to subscribe to
    
    Returns:
        dict: Response from FCM
    """
    try:
        # Subscribe tokens to topic
        response = messaging.subscribe_to_topic(tokens, topic)
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

def unsubscribe_from_topic(tokens, topic):
    """
    Unsubscribe device tokens from a specific topic
    
    Args:
        tokens (list): List of FCM device tokens
        topic (str): Topic name to unsubscribe from
    
    Returns:
        dict: Response from FCM
    """
    try:
        # Unsubscribe tokens from topic
        response = messaging.unsubscribe_from_topic(tokens, topic)
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

def send_topic_notification(topic, title, body, data=None):
    """
    Send push notification to a specific topic
    
    Args:
        topic (str): Topic name to send notification to
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
            topic=topic,
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