"""
Django production settings for eLearning project.
"""

import os
import dj_database_url
from .base import *

DEBUG = False

# Allow Railway domains and custom domains from environment
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
ALLOWED_HOSTS += [
    '.railway.app',
    '.up.railway.app',
    'django-elearning-production.up.railway.app',
]
# Remove empty strings from ALLOWED_HOSTS
ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if h]

# CSRF trusted origins for Railway
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.up.railway.app',
    'https://django-elearning-production.up.railway.app',
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Database - Railway provides DATABASE_URL
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# Redis - Railway provides REDIS_URL
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        },
    }

# Secret key from environment
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
