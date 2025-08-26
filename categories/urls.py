"""
URL configuration for categories app.

RESTful URL patterns for category CRUD operations with proper namespacing
and support for AJAX endpoints.
"""
from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    # List and filtering views
    path('', views.CategoryListView.as_view(), name='category-list'),
    
    # CRUD operations
    path('create/', views.CategoryCreateView.as_view(), name='category-create'),
    path('<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),
    
    # AJAX endpoints for dynamic functionality
    path('ajax/parents/', views.get_parent_categories_ajax, name='ajax-parent-categories'),
    
    # Bulk actions
    path('bulk-action/', views.bulk_category_action, name='bulk-action'),
]