from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Main transaction views
    path('', views.TransactionListView.as_view(), name='list'),
    path('create/', views.TransactionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='delete'),
    
    # Additional utility views
    path('stats/', views.TransactionStatsView.as_view(), name='stats'),
    
    # AJAX endpoints
    path('api/categories/', views.get_categories_by_type, name='api_categories_by_type'),
    path('api/accounts/', views.get_accounts_data, name='api_accounts_data'),
]