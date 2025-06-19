from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

def send_scheduled_notification(topic, title, body):
    """
    Send a notification at a scheduled time
    
    Args:
        topic: The topic to send to
        title: Notification title
        body: Notification body
    """
    from apis.firebase_admin import send_topic_notification
    
    current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Sending scheduled notification at {current_time} to {topic}: {title}")
    
    result = send_topic_notification(topic, title, body)
    return {
        "status": "sent", 
        "time": current_time,
        "result": result,
        "topic": topic
    }

def schedule_mission_reminder(user_id, mission_id, reminder_time):
    """
    Schedule a reminder for a mission
    
    Args:
        user_id: The user ID
        mission_id: The mission ID
        reminder_time: The time to send the reminder (ISO format string or datetime)
    """
    from companion_app.models import Children_Accounts
    import datetime
    
    try:
        # Parse the reminder time if it's a string
        if isinstance(reminder_time, str):
            reminder_datetime = datetime.datetime.fromisoformat(reminder_time)
            if reminder_datetime.tzinfo is None:
                # Make timezone-aware if it's not
                reminder_datetime = timezone.make_aware(reminder_datetime)
        else:
            # Assume it's already a datetime
            reminder_datetime = reminder_time
            
        # Get mission details
        child = Children_Accounts.objects.filter(user_id=user_id).first()
        if not child:
            return {"status": "error", "message": "Child not found"}
            
        mission = None
        for m in child.notification['missions']:
            if m['id'] == mission_id:
                mission = m
                break
                
        if not mission:
            return {"status": "error", "message": "Mission not found"}
            
        # Create a unique job ID
        job_id = f"mission_reminder_{mission_id}_{user_id}"
        
        # Schedule the notification
        scheduler.add_job(
            send_scheduled_notification,
            trigger='date',
            run_date=reminder_datetime,
            id=job_id,
            replace_existing=True,
            kwargs={
                'topic': user_id,
                'title': f"Reminder: {mission['title']}",
                'body': f"You got new mission incoming: {mission['title']}"
            }
        )
        
        logger.info(f"Scheduled reminder for mission {mission_id} at {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            "status": "scheduled",
            "message": f"Reminder scheduled for {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S')}",
            "mission_id": mission_id,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error scheduling reminder: {str(e)}")
        return {"status": "error", "message": str(e)}

def process_mission_completion(user_id, mission_id):
    """
    Process a mission completion
    
    Args:
        user_id: The user ID
        mission_id: The mission ID
    """
    from companion_app.models import Children_Accounts
    from apis.firebase_admin import send_topic_notification
    
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
        logger.error(f"Error processing mission completion: {str(e)}")
        return {"status": "error", "message": str(e)}

def start():
    """Start the scheduler if it's not already running"""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started!") 