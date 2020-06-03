from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'test123',
        'HOST': 'db',
        'POSRT': '5432'
    }
}

ASGI_APPLICATION = 'biblioteka.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('queue', 6379)],
        },
    },
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static')