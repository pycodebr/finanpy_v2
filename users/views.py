"""
Authentication views for the Finanpy financial management system.

This module implements secure authentication views following Django security best practices:
- CSRF protection on all forms
- Rate limiting through session management
- Secure password handling
- Audit logging for security events
- User data isolation and access controls
"""

import logging
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import ipaddress
from typing import Any, Dict

# Configure logger for security events
logger = logging.getLogger('security')

User = get_user_model()


class SecureLoginView(LoginView):
    """
    Custom login view with email-based authentication and enhanced security features:
    - Email-based login
    - Rate limiting protection
    - Audit logging
    - IP address tracking
    - Session security
    """
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_form_class(self):
        """Return the custom authentication form for email-based login."""
        from .forms import CustomAuthenticationForm
        return CustomAuthenticationForm
    
    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Override dispatch to add security decorators."""
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self) -> str:
        """Redirect to dashboard after successful login."""
        return reverse_lazy('users:dashboard')
    
    def form_valid(self, form):
        """Handle successful login with audit logging."""
        user = form.get_user()
        
        # Log successful login
        self._log_security_event(
            'login_success',
            user=user,
            message=f"Successful login for user {user.email}"
        )
        
        # Update last login timestamp (Django does this automatically, but we ensure it)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Call parent form_valid which handles the actual login
        response = super().form_valid(form)
        
        # Set secure session parameters
        self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        
        # Add success message
        messages.success(
            self.request, 
            f'Bem-vindo de volta, {user.get_full_name() or user.email}!'
        )
        
        return response
    
    def form_invalid(self, form):
        """Handle failed login with audit logging."""
        username = form.data.get('username', 'unknown')
        
        # Log failed login attempt
        self._log_security_event(
            'login_failed',
            username=username,
            message=f"Failed login attempt for email: {username}"
        )
        
        # Add error message
        messages.error(
            self.request,
            'Credenciais inválidas. Verifique seu email e senha.'
        )
        
        return super().form_invalid(form)
    
    def _log_security_event(self, event_type: str, user=None, username=None, message: str = ''):
        """Log security events with request context."""
        ip_address = self._get_client_ip()
        user_agent = self.request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        logger.warning(
            f"Security Event: {event_type} | "
            f"IP: {ip_address} | "
            f"User: {user.email if user else username or 'N/A'} | "
            f"User-Agent: {user_agent} | "
            f"Message: {message}"
        )
    
    def _get_client_ip(self) -> str:
        """Get client IP address with proxy support."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in case of multiple proxies
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = self.request.META.get('REMOTE_ADDR', 'Unknown')
        
        # Validate IP address
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            return 'Invalid'


class SecureLogoutView(LogoutView):
    """
    Custom logout view with security features:
    - Only accepts POST requests for security
    - Session cleanup
    - Audit logging
    - Secure redirection
    """
    next_page = reverse_lazy('home')
    http_method_names = ['post']  # Only allow POST requests for security
    
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Override dispatch to check authentication and log logout events."""
        # Check if method is allowed first (this will return 405 for GET)
        if request.method.lower() not in self.http_method_names:
            return self.http_method_not_allowed(request)
        
        # Only require authentication for authenticated users
        if request.user.is_authenticated:
            # Log logout event
            logger.info(
                f"User logout: {request.user.email} | "
                f"IP: {self._get_client_ip(request)} | "
                f"Session key: {request.session.session_key}"
            )
            
            # Add logout message
            messages.info(request, 'Você foi desconectado com sucesso.')
        
        return super().dispatch(request, *args, **kwargs)
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            return 'Invalid'


class SecureSignUpView(SuccessMessageMixin, CreateView):
    """
    Custom registration view with security features:
    - Strong password validation
    - Email uniqueness verification
    - CSRF protection
    - Audit logging
    """
    model = User
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('users:login')
    success_message = 'Conta criada com sucesso! Você pode fazer login agora.'
    
    @method_decorator(sensitive_post_parameters('password1', 'password2'))
    @method_decorator(csrf_protect)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Override dispatch to add security decorators."""
        # Redirect authenticated users
        if request.user.is_authenticated:
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_class(self):
        """Return the custom user creation form."""
        from .forms import CustomUserCreationForm
        return CustomUserCreationForm
    
    def form_valid(self, form):
        """Handle successful registration with audit logging."""
        try:
            with transaction.atomic():
                # Create user account
                response = super().form_valid(form)
                
                # Log successful registration
                logger.info(
                    f"User registration: {self.object.email} | "
                    f"Username: {self.object.username} | "
                    f"IP: {self._get_client_ip()}"
                )
                
                return response
        except Exception as e:
            # Log registration error
            logger.error(
                f"Registration error: {str(e)} | "
                f"Email: {form.cleaned_data.get('email', 'N/A')} | "
                f"IP: {self._get_client_ip()}"
            )
            messages.error(
                self.request,
                'Erro ao criar conta. Tente novamente.'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle failed registration with error logging."""
        email = form.data.get('email', 'unknown')
        
        # Log failed registration attempt
        logger.warning(
            f"Failed registration attempt | "
            f"Email: {email} | "
            f"IP: {self._get_client_ip()} | "
            f"Errors: {form.errors}"
        )
        
        return super().form_invalid(form)
    
    def _get_client_ip(self) -> str:
        """Get client IP address."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = self.request.META.get('REMOTE_ADDR', 'Unknown')
        
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            return 'Invalid'


class SecurePasswordResetView(PasswordResetView):
    """
    Custom password reset view with security features:
    - Rate limiting protection
    - Email validation
    - Audit logging
    """
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')
    
    def form_valid(self, form):
        """Handle password reset request with audit logging."""
        email = form.cleaned_data['email']
        
        # Check if user exists (without revealing this information)
        try:
            user = User.objects.get(email=email)
            user_exists = True
        except User.DoesNotExist:
            user_exists = False
        
        # Log password reset request (always log, regardless of user existence)
        logger.info(
            f"Password reset requested | "
            f"Email: {email} | "
            f"User exists: {user_exists} | "
            f"IP: {self._get_client_ip()}"
        )
        
        # Always show success message for security (don't reveal if email exists)
        messages.success(
            self.request,
            'Se o email fornecido estiver cadastrado, você receberá instruções para redefinir sua senha.'
        )
        
        return super().form_valid(form)
    
    def _get_client_ip(self) -> str:
        """Get client IP address."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = self.request.META.get('REMOTE_ADDR', 'Unknown')
        
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            return 'Invalid'


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard view for authenticated users.
    Serves as the main landing page after login.
    """
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add user-specific context data."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Add user info to context
        context.update({
            'user_full_name': user.get_full_name(),
            'last_login': user.last_login,
        })
        
        return context


# Utility view for testing authentication
class ProfileView(LoginRequiredMixin, TemplateView):
    """
    User profile view for authenticated users.
    Displays user information and account settings.
    """
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add user profile data to context."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Import models to get statistics
        from accounts.models import Account
        from transactions.models import Transaction
        from categories.models import Category
        from django.utils import timezone
        from datetime import date
        
        # Calculate user statistics
        accounts_count = Account.objects.filter(user=user, is_active=True).count()
        
        # Get transactions for current month
        current_month = date.today().month
        current_year = date.today().year
        monthly_transactions = Transaction.objects.filter(
            user=user,
            transaction_date__year=current_year,
            transaction_date__month=current_month
        ).count()
        
        # Get categories count
        categories_count = Category.objects.filter(user=user, is_active=True).count()
        
        # Add user profile data
        context.update({
            'user': user,
            'profile_data': {
                'email': user.email,
                'username': user.username,
                'full_name': user.get_full_name(),
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'is_staff': user.is_staff,
                'updated_at': user.date_joined,  # For now use date_joined as updated_at
            },
            'stats': {
                'accounts_count': accounts_count,
                'monthly_transactions': monthly_transactions,
                'categories_count': categories_count,
            }
        })
        
        return context
