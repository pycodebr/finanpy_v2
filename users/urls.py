"""
URL configuration for users app authentication views.

This module defines secure URL patterns for authentication with:
- CSRF protection on all forms
- Proper view naming for reverse URL lookup
- Security-focused URL structure
- Integration with Django's built-in auth system
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views

# App namespace for URL reversing
app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path(
        'login/',
        views.SecureLoginView.as_view(),
        name='login'
    ),
    
    path(
        'logout/',
        views.SecureLogoutView.as_view(),
        name='logout'
    ),
    
    path(
        'signup/',
        views.SecureSignUpView.as_view(),
        name='signup'
    ),
    
    # Password reset URLs following Django's standard pattern
    path(
        'password-reset/',
        views.SecurePasswordResetView.as_view(),
        name='password_reset'
    ),
    
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url='/reset/done/'
        ),
        name='password_reset_confirm'
    ),
    
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    
    # Password change URLs for authenticated users
    path(
        'password-change/',
        auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change.html',
            success_url='/password-change/done/'
        ),
        name='password_change'
    ),
    
    path(
        'password-change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'
        ),
        name='password_change_done'
    ),
    
    # User profile and dashboard
    path(
        'dashboard/',
        views.DashboardView.as_view(),
        name='dashboard'
    ),
    
    path(
        'profile/',
        views.ProfileView.as_view(),
        name='profile'
    ),
]

