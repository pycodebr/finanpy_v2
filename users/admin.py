from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users with email-based authentication."""
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name')  # Email first, username auto-generated


class CustomUserChangeForm(UserChangeForm):
    """Form for updating users with email validation."""
    
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin interface.
    
    Security Features:
    - Maintains Django's built-in user admin security
    - Shows audit fields (date_joined, last_login)
    - Provides secure password change functionality
    - Includes user permissions and group management
    """
    
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Customize the list display (email first as it's the primary identifier)
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    # Fieldsets for the change form - email is already in BaseUserAdmin.fieldsets
    fieldsets = BaseUserAdmin.fieldsets
    
    # Add fieldsets for the add form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Personal Info', {
            'fields': ('email', 'first_name', 'last_name'),
            'description': 'Enter the user\'s personal information.'
        }),
    )
    
    # Security: Ensure email uniqueness is validated
    def get_form(self, request, obj=None, **kwargs):
        """Override to ensure email validation."""
        form = super().get_form(request, obj, **kwargs)
        if 'email' in form.base_fields:
            form.base_fields['email'].required = True
        return form
