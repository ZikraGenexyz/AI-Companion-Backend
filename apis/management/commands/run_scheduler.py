from django.core.management.base import BaseCommand
import time
import logging
from apis.scheduler import scheduler, start

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

class Command(BaseCommand):
    help = 'Starts the APScheduler'

    def handle(self, *args, **kwargs):
        # Initialize the scheduler
        self.stdout.write('Initializing scheduler...')
        
        # Start the scheduler using the existing start function
        start()
        
        self.stdout.write(self.style.SUCCESS('Scheduler started. Press Ctrl+C to exit.'))
        
        try:
            # Keep the process running
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            # Shutdown the scheduler on exit
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS('Scheduler shut down successfully')) 