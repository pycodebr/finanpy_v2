from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    
    This manager handles user creation and authentication using email addresses
    instead of usernames, providing enhanced security for the financial system.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model with email-based authentication.
    
    This model provides secure email-based authentication for the Finanpy 
    financial management system, ensuring user data isolation and security.
    
    Security Features:
    - Email-based authentication (USERNAME_FIELD = 'email')
    - Unique email addresses for all users
    - Inherits Django's built-in password hashing and validation
    - Supports Django's permission and group system
    - Maintains audit trail with date_joined and last_login fields
    - Username field kept optional for backward compatibility
    """
    
    # Email as primary authentication field
    email = models.EmailField(
        'email address',
        unique=True,
        help_text='Required. Enter a valid email address.'
    )
    
    # Make username optional (since we're using email for authentication)
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text='Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    
    # Use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove username from required fields
    
    # Use custom manager
    objects = UserManager()
    
    class Meta:
        db_table = 'auth_user'  # Keep same table name for consistency
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        """Return email as string representation."""
        return self.email
        
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() or self.email
        
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]
        
    def save(self, *args, **kwargs):
        """Override save to handle username generation if not provided."""
        if not self.username and self.email:
            # Generate username from email if not provided
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            
            # Ensure username uniqueness
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            self.username = username
            
        super().save(*args, **kwargs)
