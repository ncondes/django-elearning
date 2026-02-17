"""
Django development settings for eLearning project.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',
    '.up.railway.app',
    'django-elearning-production.up.railway.app',
]

# Development-specific apps
INSTALLED_APPS += []

# Email backend for development (prints to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
