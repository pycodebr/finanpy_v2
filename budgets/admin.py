from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """
    Admin interface for Budget model with comprehensive display and filtering.
    
    Provides:
    - List view with key budget information and progress
    - Filtering by user, category, status, and date ranges
    - Search functionality
    - Read-only calculated fields display
    - Bulk actions for common operations
    """
    
    list_display = [
        'name', 
        'user', 
        'category', 
        'planned_amount_display', 
        'spent_amount_display',
        'progress_bar',
        'status_badge',
        'period_display',
        'is_active'
    ]
    
    list_filter = [
        'is_active',
        'category__category_type',
        'start_date',
        'end_date',
        'created_at',
        ('user', admin.RelatedOnlyFieldListFilter),
        ('category', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'name',
        'user__username',
        'user__email',
        'category__name',
    ]
    
    readonly_fields = [
        'spent_amount_display',
        'percentage_used_display',
        'remaining_amount_display',
        'status_display',
        'progress_bar_admin',
        'days_remaining_display',
        'created_at',
        'updated_at',
        '_cached_spent_amount',
        '_cache_updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'category', 'name', 'is_active')
        }),
        ('Budget Details', {
            'fields': ('planned_amount', 'start_date', 'end_date')
        }),
        ('Progress & Status', {
            'fields': (
                'spent_amount_display',
                'remaining_amount_display', 
                'percentage_used_display',
                'progress_bar_admin',
                'status_display',
                'days_remaining_display'
            ),
            'classes': ('collapse',)
        }),
        ('Cache Information', {
            'fields': ('_cached_spent_amount', '_cache_updated_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-start_date', 'name']
    date_hierarchy = 'start_date'
    
    actions = ['activate_budgets', 'deactivate_budgets', 'refresh_cache']
    
    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('user', 'category')
    
    def period_display(self, obj):
        """Display budget period in a readable format."""
        return f"{obj.start_date.strftime('%d/%m/%Y')} - {obj.end_date.strftime('%d/%m/%Y')}"
    period_display.short_description = 'Period'
    
    def progress_bar(self, obj):
        """Display progress bar with percentage and color coding."""
        percentage = float(obj.percentage_used)
        
        if percentage < 50:
            color = '#10B981'  # green
        elif percentage < 80:
            color = '#F59E0B'  # yellow
        elif percentage < 100:
            color = '#F97316'  # orange
        else:
            color = '#EF4444'  # red
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; '
            'text-align: center; line-height: 20px; color: white; font-size: 12px;">'
            '{}%</div></div>',
            min(percentage, 100),
            color,
            round(percentage, 1)
        )
    progress_bar.short_description = 'Progress'
    
    def progress_bar_admin(self, obj):
        """Detailed progress bar for admin detail view."""
        return self.progress_bar(obj)
    progress_bar_admin.short_description = 'Progress Bar'
    
    def status_badge(self, obj):
        """Display status with color-coded badge."""
        status = obj.status
        status_colors = {
            'ACTIVE': '#10B981',
            'EXCEEDED': '#EF4444', 
            'COMPLETED': '#6B7280',
            'INACTIVE': '#9CA3AF'
        }
        
        color = status_colors.get(status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.status_display
        )
    status_badge.short_description = 'Status'
    
    def percentage_used_display(self, obj):
        """Display percentage used with formatting."""
        return f"{obj.percentage_used}%"
    percentage_used_display.short_description = 'Percentage Used'
    
    def days_remaining_display(self, obj):
        """Display days remaining with context."""
        days = obj.days_remaining
        if days > 0:
            return f"{days} days remaining"
        elif days == 0:
            return "Ends today"
        else:
            return f"Ended {abs(days)} days ago"
    days_remaining_display.short_description = 'Time Status'
    
    def activate_budgets(self, request, queryset):
        """Bulk action to activate selected budgets."""
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            f"Successfully activated {count} budget(s)."
        )
    activate_budgets.short_description = "Activate selected budgets"
    
    def deactivate_budgets(self, request, queryset):
        """Bulk action to deactivate selected budgets."""
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Successfully deactivated {count} budget(s)."
        )
    deactivate_budgets.short_description = "Deactivate selected budgets"
    
    def refresh_cache(self, request, queryset):
        """Bulk action to refresh cache for selected budgets."""
        count = 0
        for budget in queryset:
            try:
                budget.refresh_spent_amount()
                count += 1
            except Exception:
                pass
        
        self.message_user(
            request,
            f"Successfully refreshed cache for {count} budget(s)."
        )
    refresh_cache.short_description = "Refresh cache for selected budgets"
