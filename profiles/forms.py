"""
Forms for the profiles app providing user profile management functionality.

This module implements Django forms for profile data management with:
- Custom validation for personal information
- TailwindCSS compatible field styling
- Proper error handling and user feedback
- Security considerations for user data
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .models import Profile


class ProfileForm(forms.ModelForm):
    """
    Form for editing user profile information.
    
    This form handles all profile fields with proper validation and
    user-friendly error messages. It follows the project's design system
    with TailwindCSS styling and responsive layout.
    """
    
    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name', 
            'phone',
            'birth_date',
            'bio'
        ]
        
        # Custom widgets for TailwindCSS styling
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Digite seu primeiro nome',
                'maxlength': 30
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Digite seu sobrenome',
                'maxlength': 30
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+5511999999999',
                'type': 'tel',
                'maxlength': 17
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'max': timezone.now().date().strftime('%Y-%m-%d')
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Conte um pouco sobre você...',
                'rows': 4,
                'maxlength': 500
            })
        }
        
        # Custom labels
        labels = {
            'first_name': 'Primeiro Nome',
            'last_name': 'Sobrenome',
            'phone': 'Telefone',
            'birth_date': 'Data de Nascimento',
            'bio': 'Biografia'
        }
        
        # Help text for fields
        help_texts = {
            'phone': 'Formato internacional recomendado: +5511999999999',
            'birth_date': 'Sua data de nascimento (opcional)',
            'bio': 'Uma breve descrição sobre você (máximo 500 caracteres)'
        }
        
    def clean_phone(self):
        """
        Validate phone number format and uniqueness.
        """
        phone = self.cleaned_data.get('phone')
        
        if phone:
            # Remove common formatting characters for validation
            phone_clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # Basic length validation
            if len(phone_clean) < 10:
                raise ValidationError('Número de telefone muito curto.')
            
            if len(phone_clean) > 17:
                raise ValidationError('Número de telefone muito longo.')
            
            # Check if phone contains only digits and optional + prefix
            if not phone_clean.replace('+', '').isdigit():
                raise ValidationError('Número de telefone deve conter apenas dígitos e o símbolo + opcional.')
        
        return phone
    
    def clean_birth_date(self):
        """
        Validate birth date is not in the future and reasonable age limits.
        """
        birth_date = self.cleaned_data.get('birth_date')
        
        if birth_date:
            today = timezone.now().date()
            
            # Check if birth date is in the future
            if birth_date > today:
                raise ValidationError('Data de nascimento não pode estar no futuro.')
            
            # Check for reasonable age limits (minimum 13 years old)
            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            
            if age < 13:
                raise ValidationError('Você deve ter pelo menos 13 anos para usar este serviço.')
            
            if age > 120:
                raise ValidationError('Por favor, verifique a data de nascimento inserida.')
        
        return birth_date
    
    def clean_first_name(self):
        """
        Validate first name contains only letters and spaces.
        """
        first_name = self.cleaned_data.get('first_name')
        
        if first_name:
            # Check if name contains only letters, spaces, and common accented characters
            if not all(char.isalpha() or char.isspace() or char in 'áéíóúâêîôûàèìòùäëïöüãõç' for char in first_name.lower()):
                raise ValidationError('O primeiro nome deve conter apenas letras e espaços.')
            
            # Remove extra spaces
            first_name = ' '.join(first_name.split())
        
        return first_name
    
    def clean_last_name(self):
        """
        Validate last name contains only letters and spaces.
        """
        last_name = self.cleaned_data.get('last_name')
        
        if last_name:
            # Check if name contains only letters, spaces, and common accented characters
            if not all(char.isalpha() or char.isspace() or char in 'áéíóúâêîôûàèìòùäëïöüãõç' for char in last_name.lower()):
                raise ValidationError('O sobrenome deve conter apenas letras e espaços.')
            
            # Remove extra spaces
            last_name = ' '.join(last_name.split())
        
        return last_name
    
    def clean_bio(self):
        """
        Validate biography content and length.
        """
        bio = self.cleaned_data.get('bio')
        
        if bio:
            # Remove extra whitespace
            bio = ' '.join(bio.split())
            
            # Check minimum length if provided
            if len(bio) < 10 and bio.strip():
                raise ValidationError('A biografia deve ter pelo menos 10 caracteres se fornecida.')
        
        return bio
    
    def __init__(self, *args, **kwargs):
        """
        Initialize form with additional styling and validation.
        """
        super().__init__(*args, **kwargs)
        
        # Add CSS classes for validation states
        for field_name, field in self.fields.items():
            # Add required indicator for required fields
            if field.required:
                field.widget.attrs['required'] = True
                field.label = f"{field.label} *"
            
            # Add focus and validation styling
            current_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{current_classes} focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            
            # Add error styling if field has errors
            if self.errors.get(field_name):
                field.widget.attrs['class'] = f"{field.widget.attrs['class']} border-red-500 focus:border-red-500 focus:ring-red-500"
    
    def save(self, commit=True):
        """
        Save the profile with proper data formatting.
        """
        profile = super().save(commit=False)
        
        # Format phone number consistently
        if profile.phone:
            # Basic formatting - remove spaces and ensure + prefix for international
            phone_clean = profile.phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if phone_clean and not phone_clean.startswith('+') and phone_clean.startswith('55'):
                profile.phone = f"+{phone_clean}"
            else:
                profile.phone = phone_clean
        
        # Format names - capitalize properly
        if profile.first_name:
            profile.first_name = profile.first_name.title()
        
        if profile.last_name:
            profile.last_name = profile.last_name.title()
        
        if commit:
            profile.save()
        
        return profile