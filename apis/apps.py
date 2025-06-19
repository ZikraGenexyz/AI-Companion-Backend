from django.apps import AppConfig
import sys

class ApisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apis'
    
    def ready(self):
        # Don't start scheduler when running management commands
        if 'runserver' in sys.argv or 'uwsgi' in sys.argv or 'gunicorn' in sys.argv:
            from apis.scheduler import start
            start()
