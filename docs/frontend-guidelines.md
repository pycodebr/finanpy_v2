# Frontend Guidelines - Finanpy

Este documento define os padrões e diretrizes para o desenvolvimento frontend no projeto Finanpy, incluindo HTML, CSS (TailwindCSS), JavaScript e componentes reutilizáveis.

## 🎨 Design System

### Paleta de Cores

```css
/* Core Colors */
:root {
  /* Grays - Background e Text */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  
  /* Primary - Azul */
  --blue-50: #eff6ff;
  --blue-100: #dbeafe;
  --blue-200: #bfdbfe;
  --blue-300: #93c5fd;
  --blue-400: #60a5fa;
  --blue-500: #3b82f6;
  --blue-600: #2563eb;
  --blue-700: #1d4ed8;
  --blue-800: #1e40af;
  --blue-900: #1e3a8a;
  
  /* Success - Verde */
  --green-400: #4ade80;
  --green-500: #22c55e;
  --green-600: #16a34a;
  
  /* Warning - Amarelo */
  --yellow-400: #facc15;
  --yellow-500: #eab308;
  --yellow-600: #ca8a04;
  
  /* Danger - Vermelho */
  --red-400: #f87171;
  --red-500: #ef4444;
  --red-600: #dc2626;
}
```

### Tema Escuro (Padrão)
```css
/* Dark Theme Variables */
.dark {
  --bg-primary: var(--gray-900);     /* bg-gray-900 */
  --bg-secondary: var(--gray-800);   /* bg-gray-800 */
  --bg-tertiary: var(--gray-700);    /* bg-gray-700 */
  
  --text-primary: var(--gray-50);    /* text-gray-50 */
  --text-secondary: var(--gray-300); /* text-gray-300 */
  --text-muted: var(--gray-400);     /* text-gray-400 */
  
  --border: var(--gray-700);         /* border-gray-700 */
  --border-light: var(--gray-600);   /* border-gray-600 */
  
  --accent: var(--blue-600);         /* Primary actions */
  --accent-hover: var(--blue-700);   /* Hover states */
}
```

## 🏗️ Estrutura de Templates

### Template Base
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{% block meta_description %}Sistema de gestão financeira pessoal{% endblock %}">
    <title>{% block title %}Finanpy{% endblock %}</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="{% static 'img/favicon.ico' %}">
    
    <!-- TailwindCSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        'gray-750': '#2d374d',
                        'gray-850': '#1a202c',
                    }
                }
            }
        }
    </script>
    
    <!-- Custom CSS -->
    <link href="{% static 'css/base.css' %}" rel="stylesheet">
    {% block extra_css %}{% endblock %}
</head>

<body class="bg-gray-900 text-white min-h-screen antialiased">
    <!-- Navigation -->
    {% include 'components/navbar.html' %}
    
    <!-- Messages -->
    {% if messages %}
        <div class="fixed top-20 right-4 z-50 space-y-2">
            {% for message in messages %}
                {% include 'components/toast.html' with message=message %}
            {% endfor %}
        </div>
    {% endif %}
    
    <!-- Main Content -->
    <main class="{% block main_classes %}container mx-auto px-4 py-8{% endblock %}">
        <!-- Page Header -->
        {% block page_header %}{% endblock %}
        
        <!-- Page Content -->
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    {% include 'components/footer.html' %}
    
    <!-- JavaScript -->
    <script src="{% static 'js/base.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Componentes Reutilizáveis

#### Navbar
```html
<!-- templates/components/navbar.html -->
<nav class="bg-gray-800 border-b border-gray-700 sticky top-0 z-40">
    <div class="container mx-auto px-4">
        <div class="flex justify-between items-center h-16">
            <!-- Logo -->
            <div class="flex items-center space-x-4">
                <a href="{% url 'dashboard:home' %}" class="flex items-center space-x-2">
                    <img src="{% static 'img/logo.svg' %}" alt="Finanpy" class="w-8 h-8">
                    <span class="text-xl font-bold text-white">Finanpy</span>
                </a>
            </div>
            
            <!-- Desktop Menu -->
            <div class="hidden md:flex items-center space-x-6">
                <a href="{% url 'dashboard:home' %}" 
                   class="nav-link {% if request.resolver_match.url_name == 'home' %}active{% endif %}">
                    Dashboard
                </a>
                <a href="{% url 'transactions:list' %}" 
                   class="nav-link {% if 'transactions' in request.resolver_match.namespace %}active{% endif %}">
                    Transações
                </a>
                <a href="{% url 'accounts:list' %}" 
                   class="nav-link {% if 'accounts' in request.resolver_match.namespace %}active{% endif %}">
                    Contas
                </a>
                <a href="{% url 'budgets:list' %}" 
                   class="nav-link {% if 'budgets' in request.resolver_match.namespace %}active{% endif %}">
                    Orçamentos
                </a>
                <a href="{% url 'goals:list' %}" 
                   class="nav-link {% if 'goals' in request.resolver_match.namespace %}active{% endif %}">
                    Metas
                </a>
            </div>
            
            <!-- User Menu -->
            <div class="flex items-center space-x-4">
                {% if user.is_authenticated %}
                    <div class="relative" x-data="{ open: false }">
                        <button @click="open = !open" 
                                class="flex items-center space-x-2 text-gray-300 hover:text-white">
                            <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                                {{ user.first_name|first|default:user.username|first|upper }}
                            </div>
                            <span class="hidden md:block">{{ user.first_name|default:user.username }}</span>
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                            </svg>
                        </button>
                        
                        <div x-show="open" 
                             @click.away="open = false"
                             x-transition
                             class="absolute right-0 mt-2 w-48 bg-gray-800 rounded-lg shadow-lg border border-gray-700">
                            <a href="{% url 'profiles:detail' %}" class="dropdown-link">
                                Meu Perfil
                            </a>
                            <a href="{% url 'profiles:settings' %}" class="dropdown-link">
                                Configurações
                            </a>
                            <hr class="border-gray-700">
                            <a href="{% url 'auth:logout' %}" class="dropdown-link text-red-400">
                                Sair
                            </a>
                        </div>
                    </div>
                {% else %}
                    <a href="{% url 'auth:login' %}" class="btn btn-primary">
                        Entrar
                    </a>
                {% endif %}
                
                <!-- Mobile Menu Toggle -->
                <button class="md:hidden text-gray-400 hover:text-white"
                        onclick="toggleMobileMenu()">
                    <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path>
                    </svg>
                </button>
            </div>
        </div>
        
        <!-- Mobile Menu -->
        <div id="mobile-menu" class="hidden md:hidden pb-4">
            <div class="space-y-2">
                <a href="{% url 'dashboard:home' %}" class="mobile-nav-link">Dashboard</a>
                <a href="{% url 'transactions:list' %}" class="mobile-nav-link">Transações</a>
                <a href="{% url 'accounts:list' %}" class="mobile-nav-link">Contas</a>
                <a href="{% url 'budgets:list' %}" class="mobile-nav-link">Orçamentos</a>
                <a href="{% url 'goals:list' %}" class="mobile-nav-link">Metas</a>
            </div>
        </div>
    </div>
</nav>
```

#### Card Component
```html
<!-- templates/components/card.html -->
<div class="card {% if card_class %}{{ card_class }}{% endif %}">
    {% if title %}
        <div class="card-header">
            <h3 class="card-title">{{ title }}</h3>
            {% if subtitle %}
                <p class="card-subtitle">{{ subtitle }}</p>
            {% endif %}
            {% if action_url %}
                <a href="{{ action_url }}" class="btn btn-sm btn-secondary">
                    {{ action_text|default:"Ver mais" }}
                </a>
            {% endif %}
        </div>
    {% endif %}
    
    <div class="card-body">
        {{ content }}
    </div>
    
    {% if footer %}
        <div class="card-footer">
            {{ footer }}
        </div>
    {% endif %}
</div>
```

#### Modal Component
```html
<!-- templates/components/modal.html -->
<div id="{{ modal_id }}" 
     class="fixed inset-0 z-50 hidden overflow-y-auto"
     x-data="{ open: false }"
     x-show="open"
     @keydown.escape="open = false">
    
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
         @click="open = false"></div>
    
    <!-- Modal -->
    <div class="flex min-h-screen items-center justify-center p-4">
        <div class="relative bg-gray-800 rounded-lg shadow-xl max-w-{{ size|default:'lg' }} w-full mx-4"
             @click.stop>
            
            <!-- Header -->
            <div class="flex items-center justify-between p-6 border-b border-gray-700">
                <h3 class="text-lg font-semibold text-white">{{ title }}</h3>
                <button @click="open = false" 
                        class="text-gray-400 hover:text-white">
                    <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                </button>
            </div>
            
            <!-- Body -->
            <div class="p-6">
                {{ content }}
            </div>
            
            <!-- Footer -->
            {% if footer %}
                <div class="flex justify-end space-x-3 p-6 border-t border-gray-700">
                    {{ footer }}
                </div>
            {% endif %}
        </div>
    </div>
</div>
```

## 🎯 Classes CSS Customizadas

### Base Styles
```css
/* static/css/base.css */

/* Navigation */
.nav-link {
    @apply text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200;
}

.nav-link.active {
    @apply text-white bg-gray-700;
}

.mobile-nav-link {
    @apply block text-gray-300 hover:text-white hover:bg-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200;
}

.dropdown-link {
    @apply block px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-700 transition-colors duration-200;
}

/* Buttons */
.btn {
    @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg 
           focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 
           transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
    @apply bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500;
}

.btn-secondary {
    @apply bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500;
}

.btn-success {
    @apply bg-green-600 text-white hover:bg-green-700 focus:ring-green-500;
}

.btn-warning {
    @apply bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500;
}

.btn-danger {
    @apply bg-red-600 text-white hover:bg-red-700 focus:ring-red-500;
}

.btn-outline {
    @apply bg-transparent border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white;
}

.btn-sm {
    @apply px-3 py-1.5 text-xs;
}

.btn-lg {
    @apply px-6 py-3 text-base;
}

/* Cards */
.card {
    @apply bg-gray-800 rounded-lg shadow-lg border border-gray-700 overflow-hidden;
}

.card-header {
    @apply px-6 py-4 border-b border-gray-700 flex items-center justify-between;
}

.card-title {
    @apply text-lg font-semibold text-white;
}

.card-subtitle {
    @apply text-sm text-gray-400 mt-1;
}

.card-body {
    @apply p-6;
}

.card-footer {
    @apply px-6 py-4 bg-gray-750 border-t border-gray-700;
}

/* Forms */
.form-input {
    @apply bg-gray-700 border border-gray-600 text-white placeholder-gray-400 
           rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent 
           transition-colors duration-200;
}

.form-select {
    @apply bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 
           focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.form-textarea {
    @apply bg-gray-700 border border-gray-600 text-white placeholder-gray-400 
           rounded-lg px-3 py-2 resize-none focus:ring-2 focus:ring-blue-500 
           focus:border-transparent;
}

.form-checkbox {
    @apply bg-gray-700 border-gray-600 text-blue-600 rounded 
           focus:ring-blue-500 focus:ring-offset-gray-900;
}

.form-label {
    @apply block text-sm font-medium text-gray-300 mb-2;
}

.form-error {
    @apply text-red-400 text-sm mt-1;
}

.form-help {
    @apply text-gray-400 text-sm mt-1;
}

/* Tables */
.table {
    @apply w-full divide-y divide-gray-700;
}

.table thead {
    @apply bg-gray-750;
}

.table th {
    @apply px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider;
}

.table td {
    @apply px-6 py-4 whitespace-nowrap text-sm;
}

.table tr:nth-child(even) {
    @apply bg-gray-800;
}

.table tr:nth-child(odd) {
    @apply bg-gray-850;
}

/* Status Indicators */
.status-active {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800;
}

.status-inactive {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800;
}

.status-pending {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800;
}

.status-error {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800;
}

/* Progress Bars */
.progress {
    @apply w-full bg-gray-700 rounded-full h-2;
}

.progress-bar {
    @apply bg-blue-600 h-2 rounded-full transition-all duration-300;
}

.progress-bar-success {
    @apply bg-green-600;
}

.progress-bar-warning {
    @apply bg-yellow-600;
}

.progress-bar-danger {
    @apply bg-red-600;
}

/* Alerts */
.alert {
    @apply p-4 rounded-lg border-l-4;
}

.alert-info {
    @apply bg-blue-50 border-blue-400 text-blue-700;
}

.alert-success {
    @apply bg-green-50 border-green-400 text-green-700;
}

.alert-warning {
    @apply bg-yellow-50 border-yellow-400 text-yellow-700;
}

.alert-error {
    @apply bg-red-50 border-red-400 text-red-700;
}

/* Dark mode alerts */
.dark .alert-info {
    @apply bg-blue-900 bg-opacity-50 border-blue-500 text-blue-300;
}

.dark .alert-success {
    @apply bg-green-900 bg-opacity-50 border-green-500 text-green-300;
}

.dark .alert-warning {
    @apply bg-yellow-900 bg-opacity-50 border-yellow-500 text-yellow-300;
}

.dark .alert-error {
    @apply bg-red-900 bg-opacity-50 border-red-500 text-red-300;
}

/* Animations */
.fade-in {
    animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

.slide-up {
    animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Responsive utilities */
.mobile-only {
    @apply block md:hidden;
}

.desktop-only {
    @apply hidden md:block;
}
```

## 📱 Responsive Design

### Breakpoints Strategy
```css
/* Mobile First Approach */
/* Base styles: Mobile (0-767px) */
.container {
    @apply px-4;
}

/* Tablet: 768px and up */
@media (min-width: 768px) {
    .container {
        @apply px-6;
    }
}

/* Desktop: 1024px and up */
@media (min-width: 1024px) {
    .container {
        @apply px-8;
    }
}

/* Large Desktop: 1280px and up */
@media (min-width: 1280px) {
    .container {
        @apply px-12;
    }
}
```

### Grid Responsivo
```html
<!-- Grid de Cards Responsivo -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    <!-- Cards aqui -->
</div>

<!-- Tabela Responsiva -->
<div class="overflow-x-auto">
    <table class="table">
        <!-- Conteúdo da tabela -->
    </table>
</div>

<!-- Navigation Responsiva -->
<nav class="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-6">
    <!-- Links de navegação -->
</nav>
```

## ⚡ JavaScript e Interatividade

### Base JavaScript
```javascript
// static/js/base.js

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initializeToasts();
    initializeForms();
    initializeCharts();
    
    // Setup global event listeners
    setupGlobalEventListeners();
});

// Toast notifications
function initializeToasts() {
    const toasts = document.querySelectorAll('[data-toast]');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
        
        // Close button
        const closeBtn = toast.querySelector('[data-toast-close]');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                toast.classList.add('fade-out');
                setTimeout(() => toast.remove(), 300);
            });
        }
    });
}

// Form enhancements
function initializeForms() {
    // Real-time validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearValidation);
        });
    });
    
    // Currency formatting
    const currencyInputs = document.querySelectorAll('input[data-currency]');
    currencyInputs.forEach(input => {
        input.addEventListener('input', formatCurrency);
    });
    
    // Date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', validateDate);
    });
}

// Global event listeners
function setupGlobalEventListeners() {
    // Mobile menu toggle
    window.toggleMobileMenu = function() {
        const menu = document.getElementById('mobile-menu');
        menu.classList.toggle('hidden');
    };
    
    // Confirm actions
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Tem certeza?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

// Field validation
function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    const rules = field.dataset.rules?.split('|') || [];
    
    clearValidation(field);
    
    for (const rule of rules) {
        if (rule === 'required' && !value) {
            showFieldError(field, 'Este campo é obrigatório.');
            return;
        }
        
        if (rule === 'email' && value && !isValidEmail(value)) {
            showFieldError(field, 'Email inválido.');
            return;
        }
        
        if (rule.startsWith('min:')) {
            const min = parseInt(rule.split(':')[1]);
            if (value.length < min) {
                showFieldError(field, `Mínimo de ${min} caracteres.`);
                return;
            }
        }
    }
    
    showFieldSuccess(field);
}

function clearValidation(field) {
    field.classList.remove('border-red-500', 'border-green-500');
    const errorEl = field.parentNode.querySelector('.form-error');
    if (errorEl) errorEl.remove();
}

function showFieldError(field, message) {
    field.classList.add('border-red-500');
    const errorEl = document.createElement('p');
    errorEl.className = 'form-error';
    errorEl.textContent = message;
    field.parentNode.appendChild(errorEl);
}

function showFieldSuccess(field) {
    field.classList.add('border-green-500');
}

// Utility functions
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function formatCurrency(event) {
    const input = event.target;
    let value = input.value.replace(/\D/g, '');
    value = (value / 100).toFixed(2);
    value = value.replace('.', ',');
    value = value.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
    input.value = 'R$ ' + value;
}

function validateDate(event) {
    const input = event.target;
    const date = new Date(input.value);
    const today = new Date();
    
    if (input.dataset.futureOnly && date <= today) {
        showFieldError(input, 'A data deve ser futura.');
    } else if (input.dataset.pastOnly && date >= today) {
        showFieldError(input, 'A data deve ser passada.');
    }
}

// AJAX utilities
function makeRequest(url, options = {}) {
    const defaults = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    };
    
    return fetch(url, { ...defaults, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Loading states
function showLoading(element) {
    element.disabled = true;
    element.innerHTML = '<svg class="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Carregando...';
}

function hideLoading(element, originalText) {
    element.disabled = false;
    element.innerHTML = originalText;
}
```

### Charts com Chart.js
```javascript
// static/js/charts.js

// Configuração global dos gráficos
Chart.defaults.color = '#E5E7EB'; // text-gray-200
Chart.defaults.borderColor = '#374151'; // border-gray-700
Chart.defaults.backgroundColor = 'rgba(59, 130, 246, 0.1)'; // bg-blue-600 with opacity

function createBalanceChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Saldo',
                data: data.values,
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    backgroundColor: '#1F2937',
                    titleColor: '#F9FAFB',
                    bodyColor: '#E5E7EB',
                    borderColor: '#374151',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return 'Saldo: R$ ' + context.parsed.y.toLocaleString('pt-BR', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#374151',
                    },
                    ticks: {
                        color: '#9CA3AF',
                    }
                },
                y: {
                    grid: {
                        color: '#374151',
                    },
                    ticks: {
                        color: '#9CA3AF',
                        callback: function(value) {
                            return 'R$ ' + value.toLocaleString('pt-BR');
                        }
                    }
                }
            }
        }
    });
}

function createCategoryChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: data.colors || [
                    '#3B82F6', '#EF4444', '#10B981', '#F59E0B',
                    '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
                ],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                    }
                },
                tooltip: {
                    backgroundColor: '#1F2937',
                    titleColor: '#F9FAFB',
                    bodyColor: '#E5E7EB',
                    borderColor: '#374151',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: R$ ${value.toLocaleString('pt-BR', {
                                minimumFractionDigits: 2
                            })} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}
```

## 🎨 Padrões de Interface

### Loading States
```html
<!-- Loading Button -->
<button class="btn btn-primary" data-loading>
    <span class="loading-text">Salvar</span>
    <svg class="loading-spinner hidden animate-spin h-4 w-4" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
</button>

<!-- Loading Skeleton -->
<div class="animate-pulse">
    <div class="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
    <div class="h-4 bg-gray-700 rounded w-1/2 mb-2"></div>
    <div class="h-4 bg-gray-700 rounded w-5/6"></div>
</div>
```

### Empty States
```html
<!-- Empty State -->
<div class="text-center py-12">
    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
    <h3 class="mt-2 text-sm font-medium text-gray-300">Nenhuma transação</h3>
    <p class="mt-1 text-sm text-gray-400">Comece criando sua primeira transação.</p>
    <div class="mt-6">
        <a href="{% url 'transactions:create' %}" class="btn btn-primary">
            Nova Transação
        </a>
    </div>
</div>
```

### Form Patterns
```html
<!-- Form com Validation -->
<form method="post" data-validate class="space-y-6">
    {% csrf_token %}
    
    <div>
        <label for="description" class="form-label">Descrição</label>
        <input type="text" 
               id="description" 
               name="description" 
               class="form-input w-full" 
               data-rules="required|min:3"
               placeholder="Digite a descrição">
    </div>
    
    <div>
        <label for="amount" class="form-label">Valor</label>
        <input type="text" 
               id="amount" 
               name="amount" 
               class="form-input w-full" 
               data-currency
               data-rules="required"
               placeholder="R$ 0,00">
    </div>
    
    <div class="flex justify-end space-x-3">
        <a href="{% url 'transactions:list' %}" class="btn btn-outline">
            Cancelar
        </a>
        <button type="submit" class="btn btn-primary">
            Salvar
        </button>
    </div>
</form>
```

---

Estas diretrizes garantem:
- ✅ **Consistência visual** em toda aplicação
- ✅ **Experiência responsiva** em todos dispositivos  
- ✅ **Performance otimizada** com CSS e JS eficientes
- ✅ **Acessibilidade** com foco, contraste e navegação
- ✅ **Manutenibilidade** com componentes reutilizáveis