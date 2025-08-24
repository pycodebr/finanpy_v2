# Arquivos Estáticos - FinanPy

Esta pasta contém todos os arquivos estáticos (CSS, JavaScript, imagens, fonts) do projeto FinanPy.

## Estrutura de Diretórios

```
static/
├── css/
│   └── custom.css          # Estilos customizados que complementam TailwindCSS
├── js/
│   └── main.js            # JavaScript principal da aplicação
├── images/                # Imagens estáticas (logos, ícones, etc.)
├── fonts/                 # Fontes customizadas
└── README.md             # Este arquivo
```

## Configuração

### Settings.py
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

### Context Processors
Os seguintes context processors foram adicionados ao settings.py:
- `django.template.context_processors.static`
- `django.template.context_processors.media`

### URLs (urls.py)
```python
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Uso nos Templates

### Carregar arquivos estáticos
```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/custom.css' %}">
<script src="{% static 'js/main.js' %}"></script>
<img src="{% static 'images/logo.png' %}" alt="Logo">
```

### Exemplo no base.html
```html
{% load static %}
<link rel="stylesheet" type="text/css" href="{% static 'css/custom.css' %}">
<script src="{% static 'js/main.js' %}"></script>
```

## Comandos Úteis

### Coletar arquivos estáticos para produção
```bash
python manage.py collectstatic
```

### Encontrar arquivos estáticos
```bash
python manage.py findstatic css/custom.css
```

## Arquivos Incluídos

### CSS (custom.css)
- Classes utilitárias para complementar TailwindCSS
- Estilos para componentes específicos do FinanPy
- Indicadores de status financeiro
- Estilos para gráficos e dashboards
- Scrollbar customizada para tema dark
- Estilos para impressão

### JavaScript (main.js)
- **ThemeManager**: Gerenciamento de tema dark/light
- **FinancialUtils**: Utilitários para formatação de moeda e números
- **ToastManager**: Sistema de notificações toast
- **FormValidator**: Validação de formulários
- Inicialização de elementos interativos (dropdowns, modais)

## Notas de Desenvolvimento

1. **TailwindCSS**: O projeto usa TailwindCSS via CDN. Os estilos em `custom.css` complementam o framework.

2. **Tema Dark**: O projeto está configurado para usar tema dark por padrão, mas suporta alternância.

3. **Responsividade**: Todos os estilos são responsivos e seguem o padrão mobile-first.

4. **Performance**: Arquivos são minificados em produção através do comando `collectstatic`.

5. **Versionamento**: Em produção, considere usar `ManifestStaticFilesStorage` para cache busting.

## Integração com Apps

Cada app Django pode ter sua própria pasta `static/` com subpastas nomeadas pelo app:
```
app_name/
└── static/
    └── app_name/
        ├── css/
        ├── js/
        └── images/
```

Exemplo de uso:
```html
{% static 'app_name/css/app.css' %}
```