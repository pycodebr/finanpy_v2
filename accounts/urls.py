"""
URL configuration for accounts app.

Provides RESTful URL patterns for Account CRUD operations.
All URLs require authentication and are user-scoped.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Account List View
    path('', views.AccountListView.as_view(), name='account-list'),
    
    # Account Detail View
    path('<int:pk>/', views.AccountDetailView.as_view(), name='account-detail'),
    
    # Account Create View
    path('create/', views.AccountCreateView.as_view(), name='account-create'),
    
    # Account Update View
    path('<int:pk>/edit/', views.AccountUpdateView.as_view(), name='account-update'),
    
    # Account Delete View
    path('<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account-delete'),
    
    # Utility Views (for AJAX operations)
    path('<int:pk>/update-balance/', views.AccountBalanceUpdateView.as_view(), name='account-update-balance'),
]