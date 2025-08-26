from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for Profile model.
    
    Provides a clean, organized interface for managing user profiles with
    proper field grouping, search capabilities, and filtering options.
    """
    
    list_display = [
        'get_full_name', 
        'user', 
        'phone', 
        'birth_date', 
        'created_at',
        'updated_at'
    ]
    
    list_filter = [
        'created_at',
        'updated_at',
        'birth_date'
    ]
    
    search_fields = [
        'first_name',
        'last_name', 
        'user__username',
        'user__email',
        'phone'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'birth_date', 'phone')
        }),
        ('Biography', {
            'fields': ('bio',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_full_name(self, obj):
        """Display full name in admin list view."""
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'first_name'
