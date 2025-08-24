# Guia de Setup e Instalação - Finanpy

Este guia vai te ajudar a configurar o ambiente de desenvolvimento do Finanpy do zero.

## 📋 Pré-requisitos

### Sistemas Suportados
- **Linux** (Ubuntu 20.04+, CentOS 8+)
- **macOS** (10.15+)
- **Windows** (10/11 com WSL2 recomendado)

### Software Necessário

1. **Python 3.13+**
   ```bash
   # Verificar versão
   python --version
   # ou
   python3 --version
   ```

2. **pip** (gerenciador de pacotes Python)
   ```bash
   pip --version
   ```

3. **Git**
   ```bash
   git --version
   ```

4. **Editor de código** (recomendado: VS Code, PyCharm)

## 🚀 Instalação Rápida

### 1. Clonar o repositório
```bash
git clone [URL_DO_REPOSITORIO]
cd finanpy_v2
```

### 2. Criar ambiente virtual
```bash
# Criar virtual environment
python -m venv venv

# Ativar (Linux/macOS)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar banco de dados
```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate
```

### 5. Criar superusuário
```bash
python manage.py createsuperuser
```

### 6. Executar servidor de desenvolvimento
```bash
python manage.py runserver
```

🎉 **Pronto!** Acesse http://127.0.0.1:8000

## 🔧 Configuração Detalhada

### Estrutura de Arquivos
```
finanpy_v2/
├── accounts/          # App de contas financeiras
├── budgets/           # App de orçamentos
├── categories/        # App de categorias
├── core/             # Configurações do projeto
├── docs/             # Documentação
├── goals/            # App de metas financeiras
├── profiles/         # App de perfis de usuário
├── static/           # Arquivos estáticos (CSS, JS, images)
├── templates/        # Templates globais
├── transactions/     # App de transações
├── users/           # App de usuários
├── manage.py        # Script de gerenciamento Django
├── requirements.txt # Dependências Python
└── db.sqlite3      # Banco de dados (criado automaticamente)
```

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (opcional):

```env
# .env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite é o padrão)
DATABASE_URL=sqlite:///db.sqlite3

# Email (para recuperação de senha)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Configurações de desenvolvimento
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br
```

### Configurações do Django

O arquivo `core/settings.py` já vem configurado com:

- ✅ Apps instalados
- ✅ Middleware de segurança
- ✅ Configuração de templates
- ✅ Banco SQLite
- ✅ Arquivos estáticos
- ✅ Timezone Brasil

## 🗄️ Banco de Dados

### SQLite (Desenvolvimento)
O projeto usa SQLite por padrão para desenvolvimento:
- Arquivo: `db.sqlite3`
- Localização: raiz do projeto
- Configuração automática

### Comandos Úteis
```bash
# Ver status das migrações
python manage.py showmigrations

# Criar migrações para um app específico
python manage.py makemigrations accounts

# Aplicar migrações específicas
python manage.py migrate accounts

# Reset do banco (CUIDADO!)
rm db.sqlite3
python manage.py migrate

# Backup do banco
cp db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3
```

## 👥 Dados de Teste

### Criar usuário administrador
```bash
python manage.py createsuperuser
```

### Carregar dados iniciais (quando disponível)
```bash
python manage.py loaddata fixtures/initial_data.json
```

### Popular categorias padrão
```bash
python manage.py shell

>>> from categories.models import Category
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.first()

# Criar categorias de receita
>>> Category.objects.create(user=user, name="Salário", category_type="income", color="#10B981")
>>> Category.objects.create(user=user, name="Freelance", category_type="income", color="#059669")
>>> Category.objects.create(user=user, name="Investimentos", category_type="income", color="#047857")

# Criar categorias de despesa
>>> Category.objects.create(user=user, name="Alimentação", category_type="expense", color="#EF4444")
>>> Category.objects.create(user=user, name="Transporte", category_type="expense", color="#F97316")
>>> Category.objects.create(user=user, name="Moradia", category_type="expense", color="#8B5CF6")
>>> Category.objects.create(user=user, name="Saúde", category_type="expense", color="#06B6D4")
>>> Category.objects.create(user=user, name="Educação", category_type="expense", color="#84CC16")
```

## 🛠️ Ferramentas de Desenvolvimento

### VS Code
Extensões recomendadas:
- **Python** (ms-python.python)
- **Django** (batisteo.vscode-django)
- **Tailwind CSS IntelliSense** (bradlc.vscode-tailwindcss)
- **HTML CSS Support** (ecmel.vscode-html-css)

#### Configuração VS Code
Criar `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "editor.formatOnSave": true,
    "files.associations": {
        "*.html": "django-html"
    },
    "emmet.includeLanguages": {
        "django-html": "html"
    }
}
```

### PyCharm
1. Abrir projeto
2. Configurar interpretador Python (venv/bin/python)
3. Marcar pasta como Django project
4. Configurar Django settings: `core.settings`

## 🧪 Executar Testes

```bash
# Todos os testes
python manage.py test

# Testes de um app específico
python manage.py test accounts

# Testes com cobertura (instalar coverage)
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Relatório HTML
```

### Estrutura de Testes
```
app_name/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_forms.py
│   └── test_utils.py
```

## 📱 Frontend Development

### TailwindCSS
O projeto usa TailwindCSS via CDN para desenvolvimento:

```html
<!-- Em templates/base.html -->
<script src="https://cdn.tailwindcss.com"></script>
```

Para produção, configure Tailwind localmente:
```bash
npm install -D tailwindcss
npx tailwindcss init
```

### Estrutura de Assets
```
static/
├── css/
│   ├── base.css      # Estilos base
│   └── components.css # Componentes customizados
├── js/
│   ├── base.js       # JavaScript global
│   ├── charts.js     # Configuração de gráficos
│   └── forms.js      # Interações de formulários
└── img/
    └── icons/        # Ícones customizados
```

## 🔍 Debugging

### Django Debug Toolbar
```bash
pip install django-debug-toolbar
```

Adicionar em `settings.py`:
```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

### Logs
```python
import logging

logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

## 🚨 Problemas Comuns

### 1. Erro de importação de módulos
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/finanpy_v2"
```

### 2. Erro de permissão no SQLite
```bash
chmod 664 db.sqlite3
chmod 775 .  # pasta do projeto
```

### 3. Migrações não aplicam
```bash
python manage.py migrate --fake-initial
```

### 4. Erro de secret key
```bash
# Gerar nova secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Porta 8000 em uso
```bash
# Usar porta diferente
python manage.py runserver 8001

# Matar processo na porta 8000 (Linux/macOS)
sudo lsof -t -i tcp:8000 | xargs kill -9
```

## ⚡ Comandos Úteis

```bash
# Management commands
python manage.py help                    # Lista todos comandos
python manage.py shell                   # Shell interativo Django
python manage.py dbshell                 # Shell do banco de dados
python manage.py collectstatic           # Coletar arquivos estáticos
python manage.py check                   # Verificar problemas no projeto

# Desenvolvimento
python manage.py runserver 0.0.0.0:8000  # Servidor acessível na rede
python manage.py runserver --settings=core.settings.dev  # Settings específicos

# Dados
python manage.py dumpdata > backup.json  # Backup dos dados
python manage.py loaddata backup.json    # Restaurar dados
python manage.py flush                   # Limpar banco (manter estrutura)

# Apps
python manage.py startapp new_app        # Criar novo app
```

## 🔄 Workflow de Desenvolvimento

1. **Ativar ambiente virtual**
   ```bash
   source venv/bin/activate
   ```

2. **Atualizar dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Fazer alterações no código**

4. **Criar/aplicar migrações**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Executar testes**
   ```bash
   python manage.py test
   ```

6. **Commit das alterações**
   ```bash
   git add .
   git commit -m "feat: descrição da alteração"
   ```

## 📚 Próximos Passos

Após configurar o ambiente:

1. Leia a **[Arquitetura do Projeto](./architecture.md)**
2. Consulte os **[Padrões de Código](./coding-standards.md)**
3. Explore a **[Estrutura do Banco de Dados](./database-structure.md)**
4. Veja os **[Modelos de Dados](./data-models.md)**

## 🆘 Suporte

Se encontrar problemas durante a instalação:

1. Verifique os **[Problemas Comuns](#-problemas-comuns)** acima
2. Consulte o **[Troubleshooting](./troubleshooting.md)**
3. Verifique se todas as dependências estão instaladas
4. Confirme que está usando Python 3.13+

---

**Happy Coding!** 🚀