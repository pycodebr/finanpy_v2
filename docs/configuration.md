# Configurações - Finanpy

Este documento detalha todas as configurações disponíveis no projeto Finanpy, incluindo variáveis de ambiente, settings do Django e configurações específicas.

## 🔧 Variáveis de Ambiente

### Arquivo .env
Crie um arquivo `.env` na raiz do projeto para configurações locais:

```bash
# .env
# =============================================================================
# CONFIGURAÇÕES BÁSICAS
# =============================================================================

# Ambiente de execução (development, staging, production)
ENVIRONMENT=development

# Debug mode (True apenas em desenvolvimento)
DEBUG=True

# Secret key do Django (gere uma nova para produção)
SECRET_KEY=your-super-secret-key-here

# Hosts permitidos (separados por vírgula)
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# =============================================================================
# BANCO DE DADOS
# =============================================================================

# URL do banco de dados (SQLite por padrão)
DATABASE_URL=sqlite:///db.sqlite3

# Para PostgreSQL:
# DATABASE_URL=postgres://user:password@localhost:5432/finanpy_db

# Para MySQL:
# DATABASE_URL=mysql://user:password@localhost:3306/finanpy_db

# =============================================================================
# CACHE E REDIS
# =============================================================================

# URL do Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# Cache timeout padrão (em segundos)
CACHE_TTL=300

# =============================================================================
# EMAIL
# =============================================================================

# Configurações SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Email de remetente padrão
DEFAULT_FROM_EMAIL=noreply@finanpy.com

# =============================================================================
# ARQUIVOS E STORAGE
# =============================================================================

# Diretório para arquivos de mídia
MEDIA_ROOT=/var/www/finanpy/media

# URL base para arquivos de mídia
MEDIA_URL=/media/

# AWS S3 (para produção)
USE_S3=False
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=finanpy-files
AWS_S3_REGION_NAME=us-east-1

# =============================================================================
# CONFIGURAÇÕES REGIONAIS
# =============================================================================

# Idioma padrão
LANGUAGE_CODE=pt-br

# Timezone
TIME_ZONE=America/Sao_Paulo

# Moeda padrão
DEFAULT_CURRENCY=BRL

# Formato de data padrão
DATE_FORMAT=d/m/Y

# =============================================================================
# SEGURANÇA
# =============================================================================

# HTTPS (True em produção)
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0

# Session timeout (em segundos)
SESSION_COOKIE_AGE=86400

# CSRF settings
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False

# =============================================================================
# LOGGING
# =============================================================================

# Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Arquivo de log
LOG_FILE=/var/log/finanpy/django.log

# =============================================================================
# INTEGRAÇÕES EXTERNAS
# =============================================================================

# API do Banco Central (para cotações)
BCB_API_KEY=your-bcb-api-key

# Google Analytics (opcional)
GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX

# Sentry (monitoramento de erros)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# =============================================================================
# FUNCIONALIDADES
# =============================================================================

# Habilitar notificações por email
ENABLE_EMAIL_NOTIFICATIONS=True

# Habilitar backup automático
ENABLE_AUTO_BACKUP=False

# Intervalo de backup (em horas)
BACKUP_INTERVAL_HOURS=24

# Máximo de arquivos de backup
MAX_BACKUP_FILES=7
```

## ⚙️ Settings Django

### settings.py - Configuração Principal
```python
import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# =============================================================================
# APLICAÇÕES
# =============================================================================

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Para formatação de números
    
    # Third party apps
    'crispy_forms',
    'crispy_tailwind',
    'django_extensions',
    
    # Local apps
    'core',
    'users',
    'profiles',
    'accounts',
    'categories',
    'transactions',
    'budgets',
    'goals',
]

# =============================================================================
# MIDDLEWARE
# =============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom middleware
    'core.middleware.TimezoneMiddleware',
    'core.middleware.UserPreferencesMiddleware',
]

ROOT_URLCONF = 'core.urls'

# =============================================================================
# TEMPLATES
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # Custom context processors
                'core.context_processors.site_settings',
                'core.context_processors.user_preferences',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# =============================================================================
# BANCO DE DADOS
# =============================================================================

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3',
        conn_max_age=600
    )
}

# =============================================================================
# CACHE
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': int(os.getenv('CACHE_TTL', 300)),
    }
} if os.getenv('REDIS_URL') else {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# =============================================================================
# AUTENTICAÇÃO
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Login URLs
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Session settings
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', 86400))
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# =============================================================================
# INTERNACIONALIZAÇÃO
# =============================================================================

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'pt-br')
TIME_ZONE = os.getenv('TIME_ZONE', 'America/Sao_Paulo')
USE_I18N = True
USE_TZ = True

# Formatação de data e números
DATE_FORMAT = os.getenv('DATE_FORMAT', 'd/m/Y')
DATETIME_FORMAT = 'd/m/Y H:i'
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','

# =============================================================================
# ARQUIVOS ESTÁTICOS
# =============================================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# =============================================================================
# ARQUIVOS DE MÍDIA
# =============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = os.getenv('MEDIA_ROOT', BASE_DIR / 'media')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# =============================================================================
# EMAIL
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@finanpy.com')

# =============================================================================
# LOGGING
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.getenv('LOG_FILE', BASE_DIR / 'logs' / 'django.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['file', 'console'] if DEBUG else ['file'],
        'level': os.getenv('LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'] if DEBUG else ['file'],
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'finanpy': {
            'handlers': ['file', 'console'] if DEBUG else ['file'],
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# =============================================================================
# SEGURANÇA
# =============================================================================

if not DEBUG:
    # Security settings for production
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', 31536000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Cookie security
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_HTTPONLY = True

# =============================================================================
# CONFIGURAÇÕES PERSONALIZADAS
# =============================================================================

# Moeda padrão
DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'BRL')

# Configurações de backup
ENABLE_AUTO_BACKUP = os.getenv('ENABLE_AUTO_BACKUP', 'False').lower() == 'true'
BACKUP_INTERVAL_HOURS = int(os.getenv('BACKUP_INTERVAL_HOURS', 24))
MAX_BACKUP_FILES = int(os.getenv('MAX_BACKUP_FILES', 7))

# Notificações
ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'True').lower() == 'true'

# Integrações externas
BCB_API_KEY = os.getenv('BCB_API_KEY', '')
GOOGLE_ANALYTICS_ID = os.getenv('GOOGLE_ANALYTICS_ID', '')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

### settings/development.py
```python
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']

# Disable cache in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Media files served by Django in development
MEDIA_ROOT = BASE_DIR / 'media'
```

### settings/production.py
```python
from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# PostgreSQL for production
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Redis cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Sentry error tracking
if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True
    )

# AWS S3 for static and media files
if os.getenv('USE_S3', 'False').lower() == 'true':
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    
    # Static files
    STATICFILES_STORAGE = 'core.storage_backends.StaticStorage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Media files
    DEFAULT_FILE_STORAGE = 'core.storage_backends.MediaStorage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

## 🛠️ Configurações Específicas

### Crispy Forms (TailwindCSS)
```python
# settings.py
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# Configurações customizadas
CRISPY_CLASS_CONVERTERS = {
    "textinput": "form-input",
    "select": "form-select",
    "textarea": "form-textarea",
    "checkbox": "form-checkbox",
}
```

### Django Extensions
```python
# settings.py para desenvolvimento
INSTALLED_APPS += ['django_extensions']

# Comandos úteis disponíveis:
# python manage.py shell_plus
# python manage.py graph_models -a -o models.png
# python manage.py runserver_plus
```

### Configurações de Contexto Personalizado
```python
# core/context_processors.py
from django.conf import settings

def site_settings(request):
    """Configurações globais do site."""
    return {
        'SITE_NAME': 'Finanpy',
        'SITE_VERSION': '1.0.0',
        'DEFAULT_CURRENCY': settings.DEFAULT_CURRENCY,
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'SENTRY_DSN': getattr(settings, 'SENTRY_DSN', ''),
    }

def user_preferences(request):
    """Preferências do usuário logado."""
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        return {
            'user_preferences': request.user.profile.preferences,
            'user_currency': request.user.profile.preferences.get('currency', 'BRL'),
            'user_theme': request.user.profile.preferences.get('theme', 'dark'),
        }
    return {
        'user_preferences': {},
        'user_currency': 'BRL',
        'user_theme': 'dark',
    }
```

## 🔒 Configurações de Segurança

### Content Security Policy
```python
# settings.py
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = [
    "'self'",
    "'unsafe-inline'",  # Para desenvolvimento - remover em produção
    "https://cdn.tailwindcss.com",
    "https://cdn.jsdelivr.net",
    "https://www.googletagmanager.com",
]
CSP_STYLE_SRC = [
    "'self'",
    "'unsafe-inline'",
    "https://cdn.tailwindcss.com",
    "https://fonts.googleapis.com",
]
CSP_FONT_SRC = [
    "'self'",
    "https://fonts.gstatic.com",
]
CSP_IMG_SRC = [
    "'self'",
    "data:",
    "https:",
]
```

### Configurações CORS (se necessário)
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

## 📊 Monitoramento e Métricas

### Configuração do Sentry
```python
# settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR
)

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(),
        sentry_logging,
    ],
    traces_sample_rate=0.1,
    send_default_pii=True,
    release=os.getenv('RELEASE_VERSION', 'unknown'),
    environment=os.getenv('ENVIRONMENT', 'production'),
)
```

### Health Check Endpoint
```python
# core/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Endpoint para verificação de saúde da aplicação."""
    try:
        # Verifica conexão com o banco
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': timezone.now().isoformat(),
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)
```

## 🚀 Deploy e Produção

### Configuração do Gunicorn
```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 30
keepalive = 2
```

### Configuração do Nginx
```nginx
# /etc/nginx/sites-available/finanpy
server {
    listen 80;
    server_name finanpy.com www.finanpy.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name finanpy.com www.finanpy.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location /static/ {
        alias /var/www/finanpy/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/finanpy/media/;
        expires 7d;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Script de Deploy
```bash
#!/bin/bash
# deploy.sh

set -e

echo "Starting deployment..."

# Ativar ambiente virtual
source /var/www/finanpy/venv/bin/activate

# Atualizar código
git pull origin main

# Instalar dependências
pip install -r requirements/production.txt

# Coletar arquivos estáticos
python manage.py collectstatic --noinput --settings=core.settings.production

# Aplicar migrações
python manage.py migrate --settings=core.settings.production

# Reiniciar serviços
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "Deployment completed successfully!"
```

---

Esta configuração garante:
- ✅ **Flexibilidade** entre ambientes (dev/staging/prod)
- ✅ **Segurança** robusta em produção
- ✅ **Monitoramento** completo com logs e métricas
- ✅ **Performance** otimizada com cache e CDN
- ✅ **Escalabilidade** preparada para crescimento