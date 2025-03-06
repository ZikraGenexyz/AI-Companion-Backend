"""
WSGI config for ai_companion project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_companion.settings')

if os.environ.get('ENV') == 'production':
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

application = get_wsgi_application()

app = application