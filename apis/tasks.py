from celery import shared_task
import time
from .firebase_admin import send_topic_notification

@shared_task
def add(x, y):
    """Simple task to add two numbers (for testing)"""
    return x + y

@shared_task
def send_delayed_notification(topic, title, body, delay_seconds=0):
    """
    Send a notification after a specified delay
    
    Args:
        topic: The topic to send to
        title: Notification title
        body: Notification body
        delay_seconds: Delay in seconds before sending
    """
    if delay_seconds > 0:
        time.sleep(delay_seconds)
    
    return send_topic_notification(topic, title, body)

@shared_task
def process_mission_completion(user_id, mission_id):
    """
    Process a mission completion in the background
    
    Args:
        user_id: The user ID
        mission_id: The mission ID
    """
    from companion_app.models import Children_Accounts
    
    try:
        child = Children_Accounts.objects.filter(user_id=user_id).first()
        if not child:
            return {"status": "error", "message": "Child not found"}
            
        for mission in child.notification['missions']:
            if mission['id'] == mission_id:
                mission['completed'] = True
                
                if mission['category'] == 'Homework':
                    mission['confirmation'] = False
                    mission['gpt_response'] = None
                    mission['claimable'] = True
                
                child.save()
                
                # Send notification
                send_topic_notification(
                    topic=user_id,
                    title="Mission completed!",
                    body=f"Your mission has been completed successfully!"
                )
                
                return {"status": "success", "message": "Mission marked as completed"}
                
        return {"status": "error", "message": "Mission not found"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)} 