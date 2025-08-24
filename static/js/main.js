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
    
    // Make utilities available globally
    window.FinancialUtils = FinancialUtils;
    window.FormValidator = FormValidator;
    window.toastManager = toastManager;
    
    // Initialize any interactive elements
    initializeInteractiveElements();
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

// Export for use in other files
export { ThemeManager, FinancialUtils, ToastManager, FormValidator };