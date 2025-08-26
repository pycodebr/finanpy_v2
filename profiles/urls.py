"""
URL configuration for profiles app.

This module defines URL patterns for profile management with:
- RESTful URL design
- Clear, descriptive URL names for reverse lookup
- User-scoped access patterns
- Integration with authentication system
"""

from django.urls import path
from . import views

# App namespace for URL reversing
app_name = 'profiles'

urlpatterns = [
    # Profile detail view - shows user's profile information
    path(
        '',
        views.ProfileDetailView.as_view(),
        name='detail'
    ),
    
    # Profile edit view - allows user to update profile information
    path(
        'edit/',
        views.ProfileUpdateView.as_view(),
        name='edit'
    ),
]

