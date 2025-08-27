from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for Transaction model with optimized display and filters.
    
    Features:
    - List display with essential transaction information
    - Filters for transaction type, account, category, and date
    - Search functionality across description and notes
    - User-scoped queryset for data isolation
    - Read-only fields for calculated properties
    """
    
    list_display = [
        'transaction_date',
        'description',
        'transaction_type',
        'amount_display',
        'account',
        'category',
        'user',
        'is_recurring',
        'created_at',
    ]
    
    list_filter = [
        'transaction_type',
        'is_recurring',
        'recurrence_type',
        'transaction_date',
        'account__account_type',
        'category__category_type',
        'created_at',
    ]
    
    search_fields = [
        'description',
        'notes',
        'account__name',
        'category__name',
        'user__email',
    ]
    
    date_hierarchy = 'transaction_date'
    
    ordering = ['-transaction_date', '-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user',
                'transaction_type',
                'amount',
                'description',
                'transaction_date',
            )
        }),
        ('Account & Category', {
            'fields': (
                'account',
                'category',
            )
        }),
        ('Recurring Transaction', {
            'fields': (
                'is_recurring',
                'recurrence_type',
            ),
            'classes': ('collapse',),
        }),
        ('Additional Details', {
            'fields': (
                'notes',
            ),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_list_display(self, request):
        """Customize list display based on user permissions."""
        list_display = self.list_display[:]
        
        # For non-superusers, don't show user column
        if not request.user.is_superuser:
            if 'user' in list_display:
                list_display.remove('user')
                
        return list_display
    
    def get_queryset(self, request):
        """Filter queryset based on user permissions and optimize queries."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user', 'account', 'category')
        
        # Non-superusers can only see their own transactions
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
            
        return queryset
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter foreign key choices based on current user."""
        if not request.user.is_superuser:
            if db_field.name == 'account':
                kwargs['queryset'] = db_field.remote_field.model.objects.filter(
                    user=request.user, is_active=True
                ).order_by('name')
            elif db_field.name == 'category':
                kwargs['queryset'] = db_field.remote_field.model.objects.filter(
                    user=request.user, is_active=True
                ).order_by('category_type', 'name')
            elif db_field.name == 'user':
                kwargs['queryset'] = db_field.remote_field.model.objects.filter(
                    id=request.user.id
                )
                
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Set user automatically for non-superuser staff."""
        if not request.user.is_superuser and not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)
