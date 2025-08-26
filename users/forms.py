"""
Custom authentication forms for the Finanpy financial management system.

This module implements secure authentication forms following Django security best practices:
- Strong password validation
- Email uniqueness verification
- Input sanitization and validation
- CSRF protection integration
- User-friendly error messages
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.contrib.auth.password_validation import validate_password
import re

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form with email-based authentication and enhanced security features:
    - Email field as primary authentication credential
    - Strong password validation
    - Email uniqueness validation
    - Field sanitization
    """
    
    email = forms.EmailField(
        label='Email',
        max_length=254,
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-input w-full',
                'placeholder': 'seu@email.com',
                'autocomplete': 'email',
            }
        ),
        help_text='Obrigatório. Este será seu login no sistema.'
    )
    
    first_name = forms.CharField(
        label='Nome',
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-input w-full',
                'placeholder': 'Seu nome',
                'autocomplete': 'given-name',
            }
        )
    )
    
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-input w-full',
                'placeholder': 'Seu sobrenome',
                'autocomplete': 'family-name',
            }
        )
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')  # Removed username
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remove username field from the form since we're using email authentication
        if 'username' in self.fields:
            del self.fields['username']
        
        # Customize password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input w-full',
            'placeholder': 'Senha',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input w-full',
            'placeholder': 'Confirme a senha',
            'autocomplete': 'new-password',
        })
        
        # Update field labels in Portuguese
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirmação de senha'
        self.fields['password2'].help_text = 'Digite a mesma senha para confirmação.'
    
    
    def clean_email(self):
        """Validate and sanitize email."""
        email = self.cleaned_data.get('email')
        if email:
            # Sanitize input
            email = escape(email.strip().lower())
            
            # Check if email already exists
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError(
                    'Este endereço de email já está cadastrado. '
                    'Use outro email ou faça login.'
                )
            
            # Additional email validation
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                raise ValidationError(
                    'Formato de email inválido.'
                )
        
        return email
    
    def clean_first_name(self):
        """Validate and sanitize first name."""
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            # Sanitize input
            first_name = escape(first_name.strip())
            
            # Validate name format (only letters, spaces, and common name characters)
            if not re.match(r"^[a-zA-ZÀ-ÿ\s\-']+$", first_name):
                raise ValidationError(
                    'Nome deve conter apenas letras, espaços, hífens e apóstrofos.'
                )
        
        return first_name
    
    def clean_last_name(self):
        """Validate and sanitize last name."""
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            # Sanitize input
            last_name = escape(last_name.strip())
            
            # Validate name format
            if not re.match(r"^[a-zA-ZÀ-ÿ\s\-']+$", last_name):
                raise ValidationError(
                    'Sobrenome deve conter apenas letras, espaços, hífens e apóstrofos.'
                )
        
        return last_name
    
    def clean_password1(self):
        """Enhanced password validation."""
        password1 = self.cleaned_data.get('password1')
        if password1:
            # Django's built-in password validation
            try:
                validate_password(password1)
            except ValidationError as error:
                # Translate common validation messages to Portuguese
                portuguese_messages = []
                for message in error.messages:
                    if 'too short' in message:
                        portuguese_messages.append('A senha deve ter pelo menos 8 caracteres.')
                    elif 'too common' in message:
                        portuguese_messages.append('Esta senha é muito comum.')
                    elif 'entirely numeric' in message:
                        portuguese_messages.append('A senha não pode ser totalmente numérica.')
                    elif 'similar to' in message:
                        portuguese_messages.append('A senha é muito similar às suas informações pessoais.')
                    else:
                        portuguese_messages.append(message)
                
                raise ValidationError(portuguese_messages)
            
            # Additional custom password validation
            if len(set(password1)) < 4:
                raise ValidationError(
                    'A senha deve conter pelo menos 4 caracteres diferentes.'
                )
        
        return password1
    
    def clean_password2(self):
        """Validate password confirmation."""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('As senhas não coincidem.')
        
        return password2
    
    def save(self, commit=True):
        """Save user with validated data and email as primary authentication."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # Username will be auto-generated from email in the model's save method
        
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form with email-based authentication and enhanced security features:
    - Email-based login
    - Styled form fields
    - Improved error messages
    - Input sanitization
    """
    
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        
        # Customize form fields for email authentication
        self.fields['username'].widget.attrs.update({
            'class': 'form-input w-full',
            'placeholder': 'seu@email.com',
            'autocomplete': 'email',
            'type': 'email',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input w-full',
            'placeholder': 'Senha',
            'autocomplete': 'current-password',
        })
        
        # Update field labels
        self.fields['username'].label = 'Email'
        self.fields['password'].label = 'Senha'
    
    def clean_username(self):
        """Sanitize and validate email input."""
        username = self.cleaned_data.get('username')
        if username:
            username = escape(username.strip().lower())
            
            # Validate email format
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, username):
                raise ValidationError('Digite um endereço de email válido.')
                
        return username
    
    def clean(self):
        """Override clean to provide better error messages."""
        try:
            return super().clean()
        except ValidationError:
            # Provide generic error message for security
            raise ValidationError(
                'Credenciais inválidas. Verifique seu usuário e senha.'
            )


class PasswordResetForm(forms.Form):
    """
    Custom password reset form with enhanced security features:
    - Email validation
    - Rate limiting friendly
    - Consistent user experience
    """
    
    email = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-input w-full',
                'placeholder': 'seu@email.com',
                'autocomplete': 'email',
            }
        ),
        help_text='Digite o email associado à sua conta.'
    )
    
    def clean_email(self):
        """Validate and sanitize email."""
        email = self.cleaned_data.get('email')
        if email:
            email = escape(email.strip().lower())
            
            # Validate email format
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                raise ValidationError('Formato de email inválido.')
        
        return email