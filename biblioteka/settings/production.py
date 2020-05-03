from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': os.environ['POSTGRESQL_USER'],
        'PASSWORD': os.environ['POSTGRESQL_PASSWORD'],
        'HOST': os.environ['POSTGRESQL_HOST'],
        'PORT': os.environ['POSTGRESQL_PORT'],
    }
}

STATIC_ROOT = '/var/www/biblioteka/static'