from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    # Budget CRUD URLs following RESTful patterns
    path('', views.BudgetListView.as_view(), name='list'),
    path('create/', views.BudgetCreateView.as_view(), name='create'),
    path('<int:pk>/', views.BudgetDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.BudgetUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='delete'),
    
    # AJAX endpoints for dynamic functionality
    path('api/historical-data/', views.BudgetHistoricalDataView.as_view(), name='historical_data'),
    path('api/<int:pk>/toggle-status/', views.BudgetStatusToggleView.as_view(), name='toggle_status'),
]