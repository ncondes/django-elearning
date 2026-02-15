"""
Django production settings for eLearning project.
"""

from .base import *

DEBUG = False

ALLOWED_HOSTS = []  # Add your production domain here

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
