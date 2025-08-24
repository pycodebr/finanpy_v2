# Configuração de Arquivos Estáticos e Media - FinanPy

## Visão Geral

Este documento descreve a configuração completa de arquivos estáticos e media para o sistema FinanPy, seguindo as melhores práticas do Django.

## Estrutura de Diretórios

```
finanpy_v2/
├── static/                     # Arquivos estáticos do projeto
│   ├── css/
│   │   └── custom.css         # Estilos personalizados
│   ├── js/
│   │   └── main.js           # JavaScript principal
│   ├── images/               # Imagens do projeto
│   └── fonts/                # Fontes personalizadas
├── staticfiles/              # Arquivos coletados pelo collectstatic
├── media/                    # Arquivos enviados pelos usuários
│   ├── profile_avatars/      # Avatars de perfil
│   └── transaction_receipts/ # Comprovantes de transações
└── templates/
    └── base.html            # Template base com configuração de static files
```

## Configurações no settings.py

### Arquivos Estáticos

```python
# URLs e diretórios
STATIC_URL = '/static/'                    # URL base para arquivos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'     # Diretório onde collectstatic coleta os arquivos
STATICFILES_DIRS = [                       # Diretórios adicionais para buscar arquivos
    BASE_DIR / 'static',
]

# Finders para localizar arquivos estáticos
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',      # Busca em STATICFILES_DIRS
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',  # Busca em static/ dos apps
]
```

### Arquivos Media

```python
# URLs e diretórios para uploads
MEDIA_URL = '/media/'                      # URL base para arquivos media
MEDIA_ROOT = BASE_DIR / 'media'           # Diretório onde arquivos são salvos

# Configurações de upload
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644                 # Permissões para arquivos
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
```

### Configuração de URLs (development)

No arquivo `core/urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

# Serve arquivos estáticos e media durante desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Configuração de Produção

### settings_production.py

Para produção, use as seguintes configurações:

```python
# Desabilitar DEBUG
DEBUG = False

# Storage otimizado para produção
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Diretórios para servidor web
STATIC_ROOT = '/var/www/html/finanpy/staticfiles/'
MEDIA_ROOT = '/var/www/html/finanpy/media/'

# Permissões de arquivo
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
```

### ManifestStaticFilesStorage

Esta storage class oferece:
- Cache-busting automático (adiciona hash aos nomes dos arquivos)
- Manifest de arquivos para referência
- Melhor performance em produção

## Scripts de Deployment

### deploy_static.py

Script automático para deployment de arquivos estáticos:

```bash
python deploy_static.py
```

Este script:
1. Remove arquivos estáticos antigos
2. Coleta todos os arquivos estáticos
3. Verifica se arquivos principais existem
4. Fornece instruções para próximos passos

## Template Configuration

### base.html

O template base está configurado com:

```django
{% load static %}

<!-- CSS personalizado -->
<link rel="stylesheet" type="text/css" href="{% static 'css/custom.css' %}">

<!-- JavaScript personalizado -->
<script src="{% static 'js/main.js' %}"></script>
```

### Context Processors

No settings.py, os context processors estão habilitados:

```python
'context_processors': [
    'django.template.context_processors.static',  # Adiciona STATIC_URL
    'django.template.context_processors.media',   # Adiciona MEDIA_URL
],
```

## Comandos de Gerenciamento

### Coleta de Arquivos Estáticos

```bash
# Coleta todos os arquivos estáticos
python manage.py collectstatic

# Coleta com limpeza prévia
python manage.py collectstatic --clear

# Coleta sem confirmação
python manage.py collectstatic --noinput
```

### Localizar Arquivos Estáticos

```bash
# Encontra onde está um arquivo estático específico
python manage.py findstatic css/custom.css

# Mostra apenas o primeiro resultado
python manage.py findstatic css/custom.css --first
```

## Segurança e Performance

### Headers de Segurança

Na produção, configure headers de segurança:

```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### HTTPS (quando aplicável)

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

### Configuração do Servidor Web

#### Apache

```apache
Alias /static/ /var/www/html/finanpy/staticfiles/
Alias /media/ /var/www/html/finanpy/media/

<Directory /var/www/html/finanpy/staticfiles/>
    Require all granted
    # Cache por 1 ano
    ExpiresActive On
    ExpiresDefault "access plus 1 year"
</Directory>

<Directory /var/www/html/finanpy/media/>
    Require all granted
</Directory>
```

#### Nginx

```nginx
location /static/ {
    alias /var/www/html/finanpy/staticfiles/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /var/www/html/finanpy/media/;
}
```

## Arquivos Personalizados

### CSS (static/css/custom.css)

- Classes utilitárias para componentes financeiros
- Estilos para tema escuro
- Animações customizadas
- Componentes reutilizáveis

### JavaScript (static/js/main.js)

- Gerenciamento de tema
- Utilitários financeiros (formatação de moeda, datas)
- Sistema de notificações toast
- Validações de formulário
- Componentes interativos

## Estruturas de Upload

### Profile Avatars

```python
def user_avatar_path(instance, filename):
    return f'profile_avatars/user_{instance.id}/{filename}'
```

### Transaction Receipts

```python
def transaction_receipt_path(instance, filename):
    return f'transaction_receipts/{instance.user.id}/{filename}'
```

## Testes

### Verificar Configuração

```python
# No shell do Django
from django.conf import settings
from django.contrib.staticfiles import finders

# Verificar configurações
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")

# Encontrar arquivo estático
result = finders.find('css/custom.css')
print(f"Arquivo encontrado em: {result}")
```

### Teste de URLs

```bash
# Testar serving de arquivos estáticos (desenvolvimento)
curl -I http://localhost:8000/static/css/custom.css
curl -I http://localhost:8000/static/js/main.js

# Testar serving de arquivos media (desenvolvimento)
curl -I http://localhost:8000/media/test.txt
```

## Troubleshooting

### Problemas Comuns

1. **Arquivo não encontrado (404)**
   - Verificar se `django.contrib.staticfiles` está em `INSTALLED_APPS`
   - Executar `python manage.py collectstatic`
   - Verificar se o arquivo existe no diretório correto

2. **CSS não carregando**
   - Verificar se `{% load static %}` está no template
   - Confirmar sintaxe: `{% static 'path/to/file.css' %}`
   - Verificar console do browser para erros

3. **Upload não funciona**
   - Verificar permissões do diretório `MEDIA_ROOT`
   - Confirmar configuração de URLs para media
   - Verificar se form tem `enctype="multipart/form-data"`

### Logs de Debug

```python
# Adicionar ao settings.py para debug
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.contrib.staticfiles': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Conclusão

Esta configuração fornece uma base sólida para gerenciamento de arquivos estáticos e media no FinanPy, seguindo as melhores práticas do Django para desenvolvimento e produção.