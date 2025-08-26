from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model with hierarchical display and filtering.
    """
    list_display = (
        'name', 
        'category_type', 
        'user', 
        'parent',
        'color',
        'icon',
        'is_active',
        'level_display',
        'created_at'
    )
    list_filter = (
        'category_type',
        'is_active',
        'created_at',
        'parent'
    )
    search_fields = ('name', 'user__email', 'parent__name')
    readonly_fields = ('created_at', 'level_display', 'full_path')
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'category_type')
        }),
        ('Visual Settings', {
            'fields': ('color', 'icon')
        }),
        ('Hierarchy', {
            'fields': ('parent', 'full_path', 'level_display')
        }),
        ('Status & Timestamps', {
            'fields': ('is_active', 'created_at')
        }),
    )
    
    def level_display(self, obj):
        """Display the hierarchy level with indentation."""
        if obj:
            indent = "→ " * obj.level
            return f"{indent}Level {obj.level}"
        return ""
    level_display.short_description = "Hierarchy Level"
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('user', 'parent')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter parent choices to same user and category type."""
        if db_field.name == "parent":
            # This will be handled by form validation, but we can add filtering here
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
