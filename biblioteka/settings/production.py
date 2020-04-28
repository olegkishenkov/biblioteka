from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'Wwnp2LG8NMtL0ocWQL81',
        'HOST': 'database-1.cmeyyraaskkp.us-west-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}

STATIC_ROOT = '/var/www/biblioteka/static'