"""
Production settings for FinanPy project.
"""
from .settings import *

# Security settings
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-domain.com']

# Static files production configuration
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS settings (uncomment when using HTTPS)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Static files served by web server (Apache/Nginx)
# STATIC_ROOT should point to where your web server serves static files
STATIC_ROOT = '/var/www/html/finanpy/staticfiles/'

# Media files served by web server (Apache/Nginx)  
# MEDIA_ROOT should point to where your web server serves media files
MEDIA_ROOT = '/var/www/html/finanpy/media/'

# File upload settings for production
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}