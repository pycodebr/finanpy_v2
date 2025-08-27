// Main JavaScript file for FinanPy

// Theme management
class ThemeManager {
    constructor() {
        this.init();
    }
    
    init() {
        // Initialize theme based on localStorage or system preference
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            this.setDarkMode(true);
        } else {
            this.setDarkMode(false);
        }
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.setDarkMode(e.matches);
            }
        });
    }
    
    setDarkMode(isDark) {
        if (isDark) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }
    
    toggleTheme() {
        const isDark = document.documentElement.classList.contains('dark');
        this.setDarkMode(!isDark);
    }
}

// Financial utilities
class FinancialUtils {
    static formatCurrency(amount, currency = 'BRL') {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }
    
    static formatNumber(number, decimals = 2) {
        return new Intl.NumberFormat('pt-BR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    }
    
    static formatDate(date) {
        return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
    }
    
    static formatDateTime(date) {
        return new Intl.DateTimeFormat('pt-BR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    }
}

// Toast notification system
class ToastManager {
    constructor() {
        this.container = this.createContainer();
    }
    
    createContainer() {
        const container = document.createElement('div');
        container.className = 'fixed top-4 right-4 z-50 space-y-2';
        container.id = 'toast-container';
        document.body.appendChild(container);
        return container;
    }
    
    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        
        const typeClasses = {
            success: 'bg-success-600 text-white',
            error: 'bg-danger-600 text-white',
            warning: 'bg-warning-600 text-white',
            info: 'bg-primary-600 text-white'
        };
        
        toast.className = `${typeClasses[type]} px-4 py-3 rounded-lg shadow-lg transform transition-all duration-300 opacity-0 translate-x-full max-w-sm`;
        toast.innerHTML = `
            <div class="flex items-center justify-between">
                <span class="flex-1">${message}</span>
                <button type="button" class="ml-3 text-white/70 hover:text-white" onclick="this.parentElement.parentElement.remove()">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;
        
        this.container.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.remove('opacity-0', 'translate-x-full');
        }, 10);
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.add('opacity-0', 'translate-x-full');
                setTimeout(() => {
                    toast.remove();
                }, 300);
            }, duration);
        }
    }
    
    success(message, duration = 5000) {
        this.show(message, 'success', duration);
    }
    
    error(message, duration = 5000) {
        this.show(message, 'error', duration);
    }
    
    warning(message, duration = 5000) {
        this.show(message, 'warning', duration);
    }
    
    info(message, duration = 5000) {
        this.show(message, 'info', duration);
    }
}

// Form validation utilities
class FormValidator {
    static validateRequired(value) {
        return value && value.trim() !== '';
    }
    
    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    static validateCurrency(value) {
        const numberValue = parseFloat(value);
        return !isNaN(numberValue) && numberValue >= 0;
    }
    
    static validateDate(date) {
        return !isNaN(Date.parse(date));
    }
}

// Initialize global instances
let themeManager;
let toastManager;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize managers
    themeManager = new ThemeManager();
    toastManager = new ToastManager();
    transactionManager = new TransactionManager();
    chartManager = new ChartManager();
    
    // Make utilities available globally
    window.FinancialUtils = FinancialUtils;
    window.FormValidator = EnhancedFormValidator;
    window.CurrencyFormatter = CurrencyFormatter;
    window.toastManager = toastManager;
    window.transactionManager = transactionManager;
    window.chartManager = chartManager;
    window.AjaxHelper = AjaxHelper;
    window.QuickTransactionModal = QuickTransactionModal;
    
    // Initialize any interactive elements
    initializeInteractiveElements();
    initializeTransactionFeatures();
});

function initializeInteractiveElements() {
    // Initialize dropdowns
    const dropdownButtons = document.querySelectorAll('[data-dropdown-toggle]');
    dropdownButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const targetId = this.getAttribute('data-dropdown-toggle');
            const dropdown = document.getElementById(targetId);
            if (dropdown) {
                dropdown.classList.toggle('hidden');
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        const dropdowns = document.querySelectorAll('[data-dropdown]');
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });
    });
    
    // Initialize modals
    const modalTriggers = document.querySelectorAll('[data-modal-toggle]');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const targetId = this.getAttribute('data-modal-toggle');
            const modal = document.getElementById(targetId);
            if (modal) {
                modal.classList.remove('hidden');
                modal.classList.add('flex');
            }
        });
    });
    
    // Close modals
    const modalCloses = document.querySelectorAll('[data-modal-hide]');
    modalCloses.forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-modal-hide');
            const modal = document.getElementById(targetId);
            if (modal) {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            }
        });
    });
    
    // Close modals when clicking backdrop
    const modals = document.querySelectorAll('[data-modal]');
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.add('hidden');
                this.classList.remove('flex');
            }
        });
    });
}

function initializeTransactionFeatures() {
    // Initialize currency formatting for existing inputs
    const currencyInputs = document.querySelectorAll('.currency-input input, input[name="amount"]');
    currencyInputs.forEach(input => {
        input.addEventListener('input', () => CurrencyFormatter.formatInput(input));
        input.addEventListener('blur', () => {
            if (input.value && !input.value.includes(',')) {
                const numValue = parseFloat(input.value);
                if (!isNaN(numValue)) {
                    input.value = numValue.toFixed(2).replace('.', ',');
                }
            }
        });
    });
    
    // Initialize transaction type handlers
    const typeSelects = document.querySelectorAll('select[name="transaction_type"]');
    typeSelects.forEach(select => {
        select.addEventListener('change', () => {
            transactionManager.updateCategoriesForType(select.value);
        });
    });
    
    // Initialize category preview handlers
    const categorySelects = document.querySelectorAll('select[name="category"]');
    categorySelects.forEach(select => {
        select.addEventListener('change', () => {
            transactionManager.updateCategoryPreview(select);
        });
    });
    
    // Initialize recurring transaction toggles
    const recurringCheckboxes = document.querySelectorAll('input[name="is_recurring"]');
    recurringCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', toggleRecurringFields);
    });
    
    // Initialize quick transaction modal triggers
    const quickModalTriggers = document.querySelectorAll('[data-quick-transaction]');
    quickModalTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            QuickTransactionModal.open();
        });
    });
    
    // Initialize transaction type buttons in quick modal
    const typeButtons = document.querySelectorAll('[data-transaction-type]');
    typeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const type = button.dataset.transactionType;
            const modal = new QuickTransactionModal();
            modal.setTransactionType(type);
        });
    });
    
    // Initialize enhanced search
    setupEnhancedSearch();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
}

function toggleRecurringFields() {
    const checkbox = this;
    const recurringFields = document.querySelector('#recurring-fields, .recurring-fields');
    const recurrenceTypeSelect = document.querySelector('select[name="recurrence_type"]');
    
    if (recurringFields) {
        recurringFields.classList.toggle('show', checkbox.checked);
    }
    
    if (recurrenceTypeSelect) {
        recurrenceTypeSelect.disabled = !checkbox.checked;
        recurrenceTypeSelect.required = checkbox.checked;
        
        if (!checkbox.checked) {
            recurrenceTypeSelect.value = '';
        }
    }
}

function setupEnhancedSearch() {
    const searchInputs = document.querySelectorAll('input[name="search"]');
    searchInputs.forEach(input => {
        let debounceTimer;
        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                if (this.value.length >= 3 || this.value.length === 0) {
                    // Auto-submit search form
                    const form = this.closest('form');
                    if (form) {
                        const submitBtn = form.querySelector('button[type="submit"]');
                        if (submitBtn) {
                            submitBtn.classList.add('loading');
                            setTimeout(() => form.submit(), 100);
                        }
                    }
                }
            }, 800);
        });
    });
}

function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Quick transaction modal: Ctrl/Cmd + N
        if ((e.ctrlKey || e.metaKey) && e.key === 'n' && !e.target.matches('input, textarea, select')) {
            e.preventDefault();
            QuickTransactionModal.open();
        }
        
        // Close modals: Escape
        if (e.key === 'Escape') {
            const quickModal = document.getElementById('quickTransactionModal');
            if (quickModal && !quickModal.classList.contains('hidden')) {
                QuickTransactionModal.close();
            }
        }
        
        // Submit forms: Ctrl/Cmd + Enter
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.activeElement.closest('form');
            if (activeForm) {
                e.preventDefault();
                activeForm.submit();
            }
        }
    });
}

// Global functions for backward compatibility and widget attributes
window.openQuickTransactionModal = () => QuickTransactionModal.open();
window.closeQuickTransactionModal = () => QuickTransactionModal.close();
window.setQuickTransactionType = (type) => {
    const modal = new QuickTransactionModal();
    modal.setTransactionType(type);
};

// Enhanced confirmation dialogs
window.confirmDelete = function(transactionId, description) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4';
    modal.innerHTML = `
        <div class="bg-dark-800 rounded-2xl border border-dark-700 max-w-md w-full p-6 transform scale-95 opacity-0 transition-all duration-300">
            <div class="flex items-center mb-4">
                <div class="w-12 h-12 bg-red-600/20 rounded-xl flex items-center justify-center mr-4">
                    <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                </div>
                <h3 class="text-xl font-bold text-white">Excluir Transação</h3>
            </div>
            <p class="text-gray-300 mb-6 leading-relaxed">
                Tem certeza que deseja excluir a transação <strong>"${description}"</strong>?
                <br><br>
                <span class="text-red-400 font-medium">Esta ação não pode ser desfeita.</span>
            </p>
            <div class="flex gap-3">
                <button onclick="window.location.href='/transactions/${transactionId}/delete/'" 
                        class="flex-1 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white py-3 px-4 rounded-xl font-semibold transition-all duration-300">
                    Sim, Excluir
                </button>
                <button onclick="this.closest('.fixed').remove()" 
                        class="px-6 py-3 text-gray-400 hover:text-white border border-gray-600 hover:border-gray-500 hover:bg-dark-700/50 rounded-xl transition-all duration-300 font-semibold">
                    Cancelar
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Animate in
    requestAnimationFrame(() => {
        const content = modal.querySelector('.bg-dark-800');
        content.style.opacity = '1';
        content.style.transform = 'scale(1)';
    });
    
    // Close on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            const content = modal.querySelector('.bg-dark-800');
            content.style.opacity = '0';
            content.style.transform = 'scale(0.95)';
            setTimeout(() => modal.remove(), 300);
        }
    });
};

// Transaction Management System
class TransactionManager {
    constructor() {
        this.apiEndpoints = {
            create: '/transactions/create/',
            categoriesByType: '/transactions/api/categories/',
            accounts: '/accounts/api/',  // Placeholder for accounts API
        };
        this.cache = new Map();
        this.init();
    }
    
    async init() {
        // Initialize transaction-specific functionality
        this.setupEventListeners();
        await this.loadInitialData();
    }
    
    setupEventListeners() {
        // Enhanced form handling for transaction forms
        document.addEventListener('change', this.handleFormChanges.bind(this));
        document.addEventListener('submit', this.handleFormSubmission.bind(this));
        
        // Real-time search for transaction lists
        const searchInputs = document.querySelectorAll('[data-transaction-search]');
        searchInputs.forEach(input => {
            let debounceTimer;
            input.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    this.handleSearch(e.target.value);
                }, 500);
            });
        });
    }
    
    async loadInitialData() {
        try {
            // Load accounts and categories data for quick access
            const [accounts, categories] = await Promise.all([
                this.loadAccounts(),
                this.loadCategories()
            ]);
            
            this.cache.set('accounts', accounts);
            this.cache.set('categories', categories);
        } catch (error) {
            console.error('Error loading initial transaction data:', error);
        }
    }
    
    async loadAccounts() {
        // This will be populated from Django context or API
        return window.accountsData || [];
    }
    
    async loadCategories() {
        try {
            const response = await fetch(this.apiEndpoints.categoriesByType);
            if (!response.ok) throw new Error('Failed to load categories');
            return await response.json();
        } catch (error) {
            console.error('Error loading categories:', error);
            return { INCOME: [], EXPENSE: [] };
        }
    }
    
    handleFormChanges(event) {
        const target = event.target;
        
        // Handle transaction type changes
        if (target.name === 'transaction_type') {
            this.updateCategoriesForType(target.value);
        }
        
        // Handle category changes
        if (target.name === 'category') {
            this.updateCategoryPreview(target);
        }
        
        // Handle amount formatting
        if (target.classList.contains('currency-input') || target.name === 'amount') {
            CurrencyFormatter.formatInput(target);
        }
    }
    
    async handleFormSubmission(event) {
        const form = event.target;
        
        // Handle quick transaction form
        if (form.id === 'quickTransactionForm') {
            event.preventDefault();
            await this.submitQuickTransaction(form);
        }
        
        // Handle main transaction form enhancements
        if (form.id === 'transaction-form') {
            this.prepareMainFormSubmission(form);
        }
    }
    
    async submitQuickTransaction(form) {
        try {
            const submitBtn = form.querySelector('[type="submit"]');
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
            
            // Validate form
            const validation = FormValidator.validateTransactionForm(form);
            if (!validation.isValid) {
                FormValidator.showValidationErrors(form, validation.errors);
                return;
            }
            
            // Prepare form data
            const formData = new FormData(form);
            formData.append('is_quick_modal', 'true');
            
            // Submit via AJAX
            const response = await AjaxHelper.post(this.apiEndpoints.create, formData);
            
            if (response.success) {
                toastManager.success('Transação criada com sucesso!');
                QuickTransactionModal.close();
                this.refreshTransactionList();
            } else {
                FormValidator.showValidationErrors(form, response.errors);
            }
        } catch (error) {
            console.error('Error submitting quick transaction:', error);
            toastManager.error('Erro ao criar transação. Tente novamente.');
        } finally {
            const submitBtn = form.querySelector('[type="submit"]');
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    }
    
    updateCategoriesForType(transactionType) {
        const categorySelects = document.querySelectorAll('select[name="category"]');
        const categories = this.cache.get('categories') || { INCOME: [], EXPENSE: [] };
        
        categorySelects.forEach(select => {
            // Clear existing options except placeholder
            select.innerHTML = '<option value="">Selecione uma categoria</option>';
            
            // Add categories for selected type
            if (categories[transactionType]) {
                categories[transactionType].forEach(category => {
                    const option = document.createElement('option');
                    option.value = category.id;
                    option.textContent = category.name;
                    option.dataset.icon = category.icon;
                    option.dataset.color = category.color;
                    select.appendChild(option);
                });
            }
        });
    }
    
    updateCategoryPreview(categorySelect) {
        const preview = document.querySelector('#category-preview');
        if (!preview) return;
        
        const selectedOption = categorySelect.selectedOptions[0];
        if (!selectedOption || !selectedOption.value) {
            preview.classList.remove('show');
            return;
        }
        
        const icon = preview.querySelector('.icon');
        const name = preview.querySelector('.name');
        
        if (icon && name) {
            const color = selectedOption.dataset.color || '#6B7280';
            const iconText = selectedOption.dataset.icon || '💰';
            
            icon.style.backgroundColor = color + '40';
            icon.style.border = '1px solid ' + color;
            icon.textContent = iconText;
            name.textContent = selectedOption.textContent;
            preview.classList.add('show');
        }
    }
    
    prepareMainFormSubmission(form) {
        // Unformat currency inputs before submission
        const currencyInputs = form.querySelectorAll('.currency-input input, input[name="amount"]');
        currencyInputs.forEach(input => {
            if (input.value) {
                input.value = CurrencyFormatter.unformat(input.value);
            }
        });
    }
    
    async handleSearch(searchTerm) {
        // Implement live search functionality
        if (searchTerm.length < 3 && searchTerm.length > 0) return;
        
        const transactionList = document.querySelector('[data-transaction-list]');
        if (!transactionList) return;
        
        try {
            transactionList.classList.add('loading');
            
            // This would typically make an AJAX request to filter transactions
            // For now, we'll use client-side filtering as a fallback
            this.filterTransactionsClientSide(searchTerm);
            
        } catch (error) {
            console.error('Error searching transactions:', error);
        } finally {
            transactionList.classList.remove('loading');
        }
    }
    
    filterTransactionsClientSide(searchTerm) {
        const transactionRows = document.querySelectorAll('[data-transaction-row]');
        const normalizedSearch = searchTerm.toLowerCase().trim();
        
        transactionRows.forEach(row => {
            const description = row.dataset.description || '';
            const notes = row.dataset.notes || '';
            const category = row.dataset.category || '';
            
            const searchText = (description + ' ' + notes + ' ' + category).toLowerCase();
            const isVisible = normalizedSearch === '' || searchText.includes(normalizedSearch);
            
            row.style.display = isVisible ? '' : 'none';
        });
    }
    
    refreshTransactionList() {
        // Refresh the transaction list after operations
        if (typeof window.location !== 'undefined') {
            window.location.reload();
        }
    }
}

// Enhanced Currency Formatter for Brazilian Real
class CurrencyFormatter {
    static format(amount, options = {}) {
        const { 
            currency = 'BRL', 
            locale = 'pt-BR',
            showSymbol = true,
            decimals = 2
        } = options;
        
        const formatter = new Intl.NumberFormat(locale, {
            style: showSymbol ? 'currency' : 'decimal',
            currency: currency,
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
        
        return formatter.format(amount);
    }
    
    static formatInput(input) {
        if (!input.value) return;
        
        // Remove all non-numeric characters except comma and period
        let value = input.value.replace(/[^\d,]/g, '');
        
        // Handle decimal separator
        if (value.includes(',')) {
            const parts = value.split(',');
            if (parts.length > 2) {
                // Keep only the last comma as decimal separator
                value = parts.slice(0, -1).join('') + ',' + parts[parts.length - 1];
            }
            
            // Limit decimal places to 2
            if (parts[1] && parts[1].length > 2) {
                value = parts[0] + ',' + parts[1].substring(0, 2);
            }
        }
        
        // Format with thousands separator
        const parts = value.split(',');
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        
        input.value = parts.join(',');
    }
    
    static unformat(formattedValue) {
        if (!formattedValue) return '0';
        
        // Remove currency symbol and thousands separators
        return formattedValue
            .replace(/[R$\s]/g, '')
            .replace(/\./g, '')
            .replace(',', '.');
    }
    
    static parseBrazilianNumber(value) {
        const unformatted = this.unformat(value);
        return parseFloat(unformatted) || 0;
    }
}

// Quick Transaction Modal Manager
class QuickTransactionModal {
    static instance = null;
    
    constructor() {
        if (QuickTransactionModal.instance) {
            return QuickTransactionModal.instance;
        }
        
        this.modal = null;
        this.isOpen = false;
        this.currentType = 'EXPENSE';
        QuickTransactionModal.instance = this;
    }
    
    static open() {
        const instance = new QuickTransactionModal();
        return instance.show();
    }
    
    static close() {
        const instance = new QuickTransactionModal();
        return instance.hide();
    }
    
    show() {
        this.modal = document.getElementById('quickTransactionModal');
        if (!this.modal) {
            console.error('Quick transaction modal not found');
            return;
        }
        
        this.modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        this.isOpen = true;
        
        // Animate entrance
        const content = this.modal.querySelector('.bg-dark-800, .bg-dark-800\/95');
        if (content) {
            content.style.opacity = '0';
            content.style.transform = 'scale(0.9) translateY(-20px)';
            
            requestAnimationFrame(() => {
                content.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
                content.style.opacity = '1';
                content.style.transform = 'scale(1) translateY(0)';
            });
        }
        
        // Focus on first input
        setTimeout(() => {
            const firstInput = this.modal.querySelector('input:not([type="hidden"])');
            if (firstInput) {
                firstInput.focus();
            }
        }, 350);
        
        // Set default date
        const dateInput = this.modal.querySelector('input[name="transaction_date"]');
        if (dateInput && !dateInput.value) {
            dateInput.value = new Date().toISOString().split('T')[0];
        }
    }
    
    hide() {
        if (!this.modal || !this.isOpen) return;
        
        const content = this.modal.querySelector('.bg-dark-800, .bg-dark-800\/95');
        if (content) {
            content.style.transition = 'all 0.2s ease-out';
            content.style.opacity = '0';
            content.style.transform = 'scale(0.95) translateY(10px)';
        }
        
        setTimeout(() => {
            this.modal.classList.add('hidden');
            document.body.style.overflow = '';
            this.isOpen = false;
            
            // Reset form and state
            const form = this.modal.querySelector('form');
            if (form) {
                form.reset();
                FormValidator.clearValidationErrors(form);
            }
            
            // Reset modal content styles
            if (content) {
                content.style.opacity = '';
                content.style.transform = '';
                content.style.transition = '';
            }
        }, 200);
    }
    
    setTransactionType(type) {
        this.currentType = type;
        
        // Update button states
        const buttons = this.modal.querySelectorAll('[data-transaction-type]');
        buttons.forEach(btn => {
            btn.classList.remove('active', 'expense', 'income');
            if (btn.dataset.transactionType === type) {
                btn.classList.add('active', type.toLowerCase());
            }
        });
        
        // Update categories if transaction manager is available
        if (window.transactionManager) {
            window.transactionManager.updateCategoriesForType(type);
        }
    }
}

// Enhanced Form Validator
class EnhancedFormValidator extends FormValidator {
    static validateTransactionForm(form) {
        const errors = {};
        let isValid = true;
        
        // Validate amount
        const amountInput = form.querySelector('input[name="amount"]');
        if (amountInput) {
            const amount = CurrencyFormatter.parseBrazilianNumber(amountInput.value);
            if (amount <= 0) {
                errors.amount = ['Por favor, insira um valor maior que zero.'];
                isValid = false;
            }
        }
        
        // Validate description
        const descriptionInput = form.querySelector('input[name="description"], textarea[name="description"]');
        if (descriptionInput && !descriptionInput.value.trim()) {
            errors.description = ['Por favor, insira uma descrição para a transação.'];
            isValid = false;
        }
        
        // Validate account
        const accountSelect = form.querySelector('select[name="account"]');
        if (accountSelect && !accountSelect.value) {
            errors.account = ['Por favor, selecione uma conta.'];
            isValid = false;
        }
        
        // Validate category
        const categorySelect = form.querySelector('select[name="category"]');
        if (categorySelect && !categorySelect.value) {
            errors.category = ['Por favor, selecione uma categoria.'];
            isValid = false;
        }
        
        // Validate transaction date
        const dateInput = form.querySelector('input[name="transaction_date"]');
        if (dateInput && !dateInput.value) {
            errors.transaction_date = ['Por favor, selecione a data da transação.'];
            isValid = false;
        }
        
        return { isValid, errors };
    }
    
    static showValidationErrors(form, errors) {
        // Clear previous errors
        this.clearValidationErrors(form);
        
        // Show new errors
        Object.keys(errors).forEach(field => {
            const input = form.querySelector(`[name="${field}"]`);
            if (input && errors[field] && errors[field].length > 0) {
                this.showFieldError(input, errors[field][0]);
            }
        });
    }
    
    static showFieldError(input, message) {
        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error text-red-400 text-sm mt-2';
        errorDiv.textContent = message;
        
        // Add error class to input
        input.classList.add('error');
        
        // Insert error after input
        input.parentNode.appendChild(errorDiv);
        
        // Remove error on input change
        const removeError = () => {
            input.classList.remove('error');
            errorDiv.remove();
            input.removeEventListener('input', removeError);
            input.removeEventListener('change', removeError);
        };
        
        input.addEventListener('input', removeError);
        input.addEventListener('change', removeError);
    }
    
    static clearValidationErrors(form) {
        // Remove error classes and error messages
        const errorInputs = form.querySelectorAll('.error');
        errorInputs.forEach(input => input.classList.remove('error'));
        
        const errorMessages = form.querySelectorAll('.form-error');
        errorMessages.forEach(msg => msg.remove());
    }
}

// AJAX Helper for Django Communication
class AjaxHelper {
    static async request(url, options = {}) {
        const defaults = {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        };
        
        // Add CSRF token for non-GET requests
        if (options.method && options.method !== 'GET') {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            if (csrfToken) {
                defaults.headers['X-CSRFToken'] = csrfToken;
            }
        }
        
        // Handle FormData
        if (options.body instanceof FormData) {
            delete defaults.headers['Content-Type'];
        }
        
        const config = { ...defaults, ...options };
        
        try {
            const response = await fetch(url, config);
            
            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                if (response.ok) {
                    return { success: true, ...data };
                } else {
                    return { success: false, ...data };
                }
            }
            
            // Handle non-JSON responses
            if (response.ok) {
                return { success: true };
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        } catch (error) {
            console.error('AJAX request failed:', error);
            return { 
                success: false, 
                error: error.message,
                errors: { __all__: ['Erro de conexão. Tente novamente.'] }
            };
        }
    }
    
    static async get(url, params = {}) {
        const searchParams = new URLSearchParams(params);
        const fullUrl = searchParams.toString() ? `${url}?${searchParams}` : url;
        return this.request(fullUrl);
    }
    
    static async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: data instanceof FormData ? data : JSON.stringify(data)
        });
    }
    
    static async put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: data instanceof FormData ? data : JSON.stringify(data)
        });
    }
    
    static async delete(url) {
        return this.request(url, { method: 'DELETE' });
    }
}

// Chart Manager for Financial Visualizations (requires Chart.js)
class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#E5E7EB',
                        font: {
                            family: 'Inter, sans-serif',
                            size: 12
                        }
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        color: '#9CA3AF',
                        callback: function(value) {
                            return CurrencyFormatter.format(value);
                        }
                    },
                    grid: {
                        color: '#374151'
                    }
                },
                x: {
                    ticks: {
                        color: '#9CA3AF'
                    },
                    grid: {
                        color: '#374151'
                    }
                }
            }
        };
    }
    
    createBalanceTrendChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || typeof Chart === 'undefined') return null;
        
        const config = {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Saldo',
                    data: data.values,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    title: {
                        display: true,
                        text: 'Evolução do Saldo',
                        color: '#F9FAFB',
                        font: {
                            size: 16,
                            family: 'Inter, sans-serif',
                            weight: 600
                        }
                    }
                }
            }
        };
        
        const chart = new Chart(canvas, config);
        this.charts.set(canvasId, chart);
        return chart;
    }
    
    createCategoryBreakdownChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || typeof Chart === 'undefined') return null;
        
        const config = {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        '#EF4444', '#F97316', '#EAB308', '#22C55E',
                        '#06B6D4', '#3B82F6', '#8B5CF6', '#EC4899'
                    ],
                    borderColor: '#1F2937',
                    borderWidth: 2
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    title: {
                        display: true,
                        text: 'Gastos por Categoria',
                        color: '#F9FAFB',
                        font: {
                            size: 16,
                            family: 'Inter, sans-serif',
                            weight: 600
                        }
                    }
                }
            }
        };
        
        const chart = new Chart(canvas, config);
        this.charts.set(canvasId, chart);
        return chart;
    }
    
    createIncomeExpenseChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || typeof Chart === 'undefined') return null;
        
        const config = {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Receitas',
                        data: data.income,
                        backgroundColor: 'rgba(16, 185, 129, 0.8)',
                        borderColor: '#10B981',
                        borderWidth: 1
                    },
                    {
                        label: 'Despesas',
                        data: data.expenses,
                        backgroundColor: 'rgba(239, 68, 68, 0.8)',
                        borderColor: '#EF4444',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    ...this.defaultOptions.plugins,
                    title: {
                        display: true,
                        text: 'Receitas vs Despesas',
                        color: '#F9FAFB',
                        font: {
                            size: 16,
                            family: 'Inter, sans-serif',
                            weight: 600
                        }
                    }
                },
                scales: {
                    ...this.defaultOptions.scales,
                    y: {
                        ...this.defaultOptions.scales.y,
                        beginAtZero: true
                    }
                }
            }
        };
        
        const chart = new Chart(canvas, config);
        this.charts.set(canvasId, chart);
        return chart;
    }
    
    destroyChart(canvasId) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.destroy();
            this.charts.delete(canvasId);
        }
    }
    
    destroyAllCharts() {
        this.charts.forEach(chart => chart.destroy());
        this.charts.clear();
    }
}

// Global instances
let transactionManager;
let chartManager;

// Export for use in other files
export { ThemeManager, FinancialUtils, ToastManager, FormValidator, TransactionManager, CurrencyFormatter, QuickTransactionModal, EnhancedFormValidator, AjaxHelper, ChartManager };