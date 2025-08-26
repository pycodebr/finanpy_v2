from django.contrib import admin
from django.utils.html import format_html
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """
    Admin interface for Account model with optimized display and filtering.
    
    Provides comprehensive management interface for financial accounts including
    user filtering, balance display formatting, and efficient querying.
    """
    
    # List display configuration
    list_display = [
        'name',
        'get_account_type_display',
        'formatted_balance',
        'currency',
        'user',
        'is_active',
        'created_at',
    ]
    
    # Filtering options
    list_filter = [
        'account_type',
        'currency',
        'is_active',
        'created_at',
        'updated_at',
    ]
    
    # Search functionality
    search_fields = [
        'name',
        'user__email',
        'user__first_name',
        'user__last_name',
    ]
    
    # Ordering
    ordering = ['-created_at']
    
    # Fields to display in the detail view
    fields = [
        'user',
        'name',
        'account_type',
        'balance',
        'currency',
        'is_active',
        'created_at',
        'updated_at',
    ]
    
    # Read-only fields
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    
    # Optimize database queries
    list_select_related = ['user']
    
    # Items per page
    list_per_page = 25
    
    # Enable date hierarchy navigation
    date_hierarchy = 'created_at'
    
    def formatted_balance(self, obj):
        """Display balance with currency formatting and color coding."""
        if obj.balance < 0:
            color = 'red'
        elif obj.balance == 0:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.balance_display
        )
    formatted_balance.short_description = 'Balance'
    formatted_balance.admin_order_field = 'balance'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for user data."""
        return super().get_queryset(request).select_related('user')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize foreign key fields in forms."""
        if db_field.name == 'user':
            # For superusers, show all users; for staff, limit appropriately
            if request.user.is_superuser:
                pass  # Show all users
            else:
                # Could limit to specific users based on permissions
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
