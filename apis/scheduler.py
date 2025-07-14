from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from django.conf import settings
import logging
import pytz
import uuid
import time
import functools

logger = logging.getLogger(__name__)

# Set Jakarta timezone
JAKARTA_TZ = pytz.timezone('Asia/Jakarta')

# Create scheduler instance with explicit timezone and optimized settings
scheduler = BackgroundScheduler({
    'apscheduler.jobstores.default': {
        'class': 'django_apscheduler.jobstores:DjangoJobStore'
    },
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': 20
    },
    'apscheduler.job_defaults.coalesce': True,
    'apscheduler.job_defaults.max_instances': 10,
    'apscheduler.misfire_grace_time': 60,
    'timezone': JAKARTA_TZ
})


# Define retry logic as a separate function instead of a decorator
def retry_on_failure(max_retries=3):
    """
    Retry a function on failure
    
    Args:
        max_retries: Maximum number of retry attempts
    """
    attempts = 0
    def _retry_on_failure(func, *args, **kwargs):
        nonlocal attempts
        while attempts < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempts += 1
                logger.error(f"Error in job (attempt {attempts}/{max_retries}): {str(e)}")
                if attempts >= max_retries:
                    logger.error(f"Job failed after {max_retries} attempts")
                    raise
                time.sleep(2 ** attempts)  # Exponential backoff
    return _retry_on_failure

def schedule_prioritized_job(func, trigger, **kwargs):
    """
    Schedule a job with priority handling
    
    Args:
        func: The function to execute
        trigger: The trigger type ('date', 'interval', 'cron')
        **kwargs: Additional arguments for scheduler.add_job
    """
    priority = kwargs.pop('priority', 5)  # Default priority (1-10, 10 being highest)
    
    # Add job with priority in the job ID
    job_id = kwargs.get('id', f"job_{uuid.uuid4()}")
    priority_job_id = f"p{priority}_{job_id}"
    
    kwargs['id'] = priority_job_id
    
    return scheduler.add_job(func, trigger, **kwargs)

def send_scheduled_notification(topic, title, body, category):
    """
    Send a notification at a scheduled time
    
    Args:
        topic: The topic to send to
        title: Notification title
        body: Notification body
    """
    from apis.firebase_admin import send_topic_notification
    
    try:
        current_time = timezone.now().astimezone(JAKARTA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Sending scheduled notification at {current_time} to {topic}: {title}")
        
        result = send_topic_notification(topic, title, body, data={"category": category})
        return {
            "status": "sent", 
            "time": current_time,
            "result": result,
            "topic": topic
        }
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        # Retry up to 3 times with exponential backoff
        for attempt in range(1, 4):
            try:
                logger.info(f"Retrying notification (attempt {attempt}/3)")
                time.sleep(2 ** attempt)  # Exponential backoff
                result = send_topic_notification(topic, title, body, data={"category": "mission"})
                return {
                    "status": "sent", 
                    "time": current_time,
                    "result": result,
                    "topic": topic
                }
            except Exception as retry_error:
                logger.error(f"Retry {attempt} failed: {str(retry_error)}")
        
        # If all retries fail, return error
        return {
            "status": "error",
            "message": str(e)
        }

def schedule_mission_reminder(user_id, mission_id, reminder_time, category, title, body):
    """
    Schedule a reminder for a mission
    
    Args:
        user_id: The user ID
        mission_id: The mission ID
        reminder_time: The time to send the reminder (ISO format string or datetime)
        category: The notification category
        title: The notification title
        body: The notification body
    """
    from companion_app.models import Children_Accounts
    import datetime
    
    try:
        # Parse the reminder time if it's a string
        if isinstance(reminder_time, str):
            reminder_datetime = datetime.datetime.fromisoformat(reminder_time)
            if reminder_datetime.tzinfo is None:
                # Make timezone-aware if it's not
                reminder_datetime = JAKARTA_TZ.localize(reminder_datetime)
        else:
            # Assume it's already a datetime
            reminder_datetime = reminder_time
            if reminder_datetime.tzinfo is None:
                reminder_datetime = JAKARTA_TZ.localize(reminder_datetime)
            else:
                # Ensure the datetime is in Jakarta timezone
                reminder_datetime = reminder_datetime.astimezone(JAKARTA_TZ)
            
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
        
        # Schedule the notification with priority
        # Higher priority for soon-to-be-due missions
        time_until_due = reminder_datetime - timezone.now().astimezone(JAKARTA_TZ)
        priority = 5  # Default priority
        
        # Adjust priority based on how soon the mission is due
        if time_until_due.total_seconds() < 3600:  # Less than 1 hour
            priority = 10  # Highest priority
        elif time_until_due.total_seconds() < 86400:  # Less than 24 hours
            priority = 8  # High priority
        
        # Use direct function reference instead of wrapped function
        scheduler.add_job(
            send_scheduled_notification,
            trigger='date',
            run_date=reminder_datetime,
            id=job_id,
            replace_existing=True,
            kwargs={
                'topic': user_id,
                'title': title,
                'body': body,
                'category': category
            }
        )
        
        logger.info(f"Scheduled reminder for mission {mission_id} at {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S')} with priority {priority}")
        
        return {
            "status": "scheduled",
            "message": f"Reminder scheduled for {reminder_datetime.strftime('%Y-%m-%d %H:%M:%S')}",
            "mission_id": mission_id,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error scheduling reminder: {str(e)}")
        return {"status": "error", "message": str(e)}

def cancel_mission_reminder(user_id, mission_id):
    """
    Cancel a scheduled mission reminder
    
    Args:
        user_id: The user ID
        mission_id: The mission ID
        
    Returns:
        dict: Status of the cancellation
    """
    try:
        # Create the same job ID format used when scheduling
        job_id = f"mission_reminder_{mission_id}_{user_id}"
        
        # Check if the job exists
        job = scheduler.get_job(job_id)
        
        if job:
            # Remove the job
            scheduler.remove_job(job_id)
            logger.info(f"Cancelled scheduled reminder for mission {mission_id} for user {user_id}")
            return {
                "status": "cancelled",
                "message": f"Reminder cancelled successfully",
                "mission_id": mission_id,
                "user_id": user_id
            }
        else:
            logger.info(f"No scheduled reminder found for mission {mission_id}")
            return {
                "status": "not_found",
                "message": f"No scheduled reminder found for this mission",
                "mission_id": mission_id,
                "user_id": user_id
            }
    except Exception as e:
        logger.error(f"Error cancelling reminder: {str(e)}")
        return {"status": "error", "message": str(e)}

def cancel_all_user_reminders(user_id):
    """
    Cancel all scheduled reminders for a specific user
    
    Args:
        user_id: The user ID
        
    Returns:
        dict: Status of the cancellation and count of cancelled jobs
    """
    try:
        # Get all jobs
        jobs = scheduler.get_jobs()
        
        # Filter jobs for this user
        user_job_ids = []
        for job in jobs:
            if job.id.startswith(f"mission_reminder_") and job.id.endswith(f"_{user_id}"):
                user_job_ids.append(job.id)
        
        # Remove all matching jobs
        cancelled_count = 0
        for job_id in user_job_ids:
            scheduler.remove_job(job_id)
            cancelled_count += 1
        
        logger.info(f"Cancelled {cancelled_count} scheduled reminders for user {user_id}")
        return {
            "status": "cancelled",
            "message": f"Cancelled {cancelled_count} scheduled reminders",
            "user_id": user_id,
            "count": cancelled_count
        }
    except Exception as e:
        logger.error(f"Error cancelling user reminders: {str(e)}")
        return {"status": "error", "message": str(e)}

def list_scheduled_reminders(user_id=None):
    """
    List all scheduled reminders, optionally filtered by user_id
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        list: List of scheduled jobs with details
    """
    try:
        jobs = scheduler.get_jobs()
        result = []
        
        for job in jobs:
            # Only include mission reminders
            if job.id.startswith("mission_reminder_"):
                # Extract job details
                job_info = {
                    "job_id": job.id,
                    "next_run_time": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else None,
                    "kwargs": job.kwargs
                }
                
                # Filter by user_id if provided
                if user_id is None or (user_id and job.id.endswith(f"_{user_id}")):
                    result.append(job_info)
        
        return result
    except Exception as e:
        logger.error(f"Error listing reminders: {str(e)}")
        return []

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
        logger.info("APScheduler started with optimized settings for hundreds of users!") 