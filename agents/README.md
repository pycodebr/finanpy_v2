# Agentes de IA - Time de Desenvolvimento Finanpy

Esta pasta contém os agentes especialistas em diferentes áreas do desenvolvimento do projeto Finanpy. Cada agente possui conhecimento profundo da stack tecnológica específica e segue os padrões estabelecidos no projeto.

## 📋 Índice de Agentes

### 🏗️ Arquitetura e Backend

#### [**Django Backend Specialist**](./django-backend-specialist.md)
- **Stack**: Python 3.13+, Django 5.2+, SQLite
- **Especialidade**: Models, Views, Forms, URLs, Migrations, Signals
- **Quando usar**: Criação/modificação de models, implementação de views, configuração de apps Django
- **MCP Context7**: Django, Python ORM patterns

#### [**Database Architect**](./database-architect.md)
- **Stack**: SQLite, Django ORM, Database Design
- **Especialidade**: Schema design, migrações, otimização de queries, índices
- **Quando usar**: Design de banco de dados, otimização de performance, troubleshooting de queries
- **MCP Context7**: Database design patterns, SQL optimization

### 🎨 Frontend e UI/UX

#### [**TailwindCSS UI Developer**](./tailwindcss-ui-developer.md)
- **Stack**: TailwindCSS, HTML5, Responsive Design
- **Especialidade**: Componentes responsivos, dark theme, mobile-first design
- **Quando usar**: Criação de interfaces, componentes reutilizáveis, ajustes de design
- **MCP Context7**: TailwindCSS, CSS best practices

#### [**Django Templates Specialist**](./django-templates-specialist.md)
- **Stack**: Django Template Language, Template inheritance, Context processors
- **Especialidade**: Template structure, components, template tags, filters
- **Quando usar**: Estruturação de templates, criação de template tags customizados
- **MCP Context7**: Django templates, Jinja2 patterns

#### [**JavaScript Interactions Developer**](./javascript-interactions-developer.md)
- **Stack**: Vanilla JavaScript, Chart.js, AJAX, DOM manipulation
- **Especialidade**: Interações frontend, gráficos financeiros, validações client-side
- **Quando usar**: Funcionalidades JavaScript, integração com APIs, gráficos dinâmicos
- **MCP Context7**: JavaScript ES6+, Chart.js, AJAX patterns

### 🔐 Segurança e Autenticação

#### [**Authentication & Security Specialist**](./authentication-security-specialist.md)
- **Stack**: Django Auth, Session management, CSRF protection
- **Especialidade**: Sistema de usuários, permissões, segurança de dados financeiros
- **Quando usar**: Implementação de autenticação, configurações de segurança, auditoria
- **MCP Context7**: Django security, Authentication patterns

### 🧪 Qualidade e Testes

#### [**QA & Testing Engineer**](./qa-testing-engineer.md)
- **Stack**: Django TestCase, pytest, Coverage, Unit/Integration tests
- **Especialidade**: Estratégias de teste, TDD, automação de QA
- **Quando usar**: Criação de testes, validação de funcionalidades, garantia de qualidade
- **MCP Context7**: Python testing, Django testing patterns

### 📊 Dados e Relatórios

#### [**Financial Data Analyst**](./financial-data-analyst.md)
- **Stack**: Django ORM, Python data processing, Chart.js
- **Especialidade**: Cálculos financeiros, agregações, relatórios, dashboards
- **Quando usar**: Lógica de negócio financeiro, métricas, análises, visualizações
- **MCP Context7**: Financial calculations, Data aggregation patterns

### ⚙️ DevOps e Configuração

#### [**DevOps & Configuration Manager**](./devops-configuration-manager.md)
- **Stack**: Django settings, Environment variables, Deployment
- **Especialidade**: Configurações de ambiente, deploy, monitoramento, performance
- **Quando usar**: Setup de ambiente, configurações de produção, otimização de performance
- **MCP Context7**: Django deployment, Environment management

### 🎯 Produto e Experiência

#### [**Product & UX Strategist**](./product-ux-strategist.md)
- **Stack**: User Experience, Product Management, Requirements analysis
- **Especialidade**: Análise de requisitos, fluxos de usuário, estratégia de produto
- **Quando usar**: Definição de funcionalidades, análise de UX, priorização de features
- **MCP Context7**: UX patterns, Product management frameworks

## 🔄 Fluxo de Trabalho dos Agentes

### 1. **Planejamento de Feature**
```
Product & UX Strategist → Django Backend Specialist → Database Architect
```

### 2. **Implementação de Interface**
```
TailwindCSS UI Developer → Django Templates Specialist → JavaScript Interactions Developer
```

### 3. **Implementação de Backend**
```
Database Architect → Django Backend Specialist → Authentication & Security Specialist
```

### 4. **Relatórios e Dashboards**
```
Financial Data Analyst → JavaScript Interactions Developer → TailwindCSS UI Developer
```

### 5. **Qualidade e Deploy**
```
QA & Testing Engineer → DevOps & Configuration Manager
```

## 🎯 Guidelines de Uso

### Quando usar cada agente:

1. **Nova Feature Completa**: Comece com Product & UX Strategist
2. **Bug Fix**: Identifique o agente da área específica
3. **Performance Issues**: DevOps & Configuration Manager ou Database Architect
4. **UI/UX Improvements**: TailwindCSS UI Developer ou Django Templates Specialist
5. **Security Issues**: Authentication & Security Specialist
6. **Data/Relatórios**: Financial Data Analyst
7. **Testes**: QA & Testing Engineer

### Colaboração entre Agentes:

- **Backend + Frontend**: Django Backend + TailwindCSS UI + Django Templates
- **Segurança + Backend**: Authentication & Security + Django Backend  
- **Dados + Visualização**: Financial Data Analyst + JavaScript Interactions
- **Qualidade + Todos**: QA & Testing pode trabalhar com qualquer agente

## 📚 Padrões Compartilhados

Todos os agentes seguem:
- **Documentação**: Padrões definidos em `/docs/`
- **Coding Standards**: PEP 8, convenções do projeto
- **Arquitetura**: MVT Django, modular apps
- **Stack**: Python 3.13+, Django 5.2+, TailwindCSS, SQLite
- **Tema**: Dark theme, design responsivo
- **MCP Context7**: Utilizat