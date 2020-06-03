"""
ASGI config for biblioteka project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""
import logging
import os
import django

from channels.routing import get_default_application

from dotenv import load_dotenv

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteka.settings.local')
load_dotenv()
django.setup()
application = get_default_application()
logger = logging.getLogger(__name__)
logger.debug(__name__+' '+os.environ['DJANGO_SETTINGS_MODULE'])
logger.propagate = True