from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator


class Profile(models.Model):
    """
    User profile model extending the base User model with additional personal information.
    
    This model maintains a one-to-one relationship with the User model to store
    extended profile information such as personal details, contact information,
    and biography. It follows the project's data isolation pattern by being
    directly linked to a user.
    
    Fields:
    - user: OneToOneField linking to the custom User model
    - first_name: User's first name (optional)
    - last_name: User's last name (optional)
    - phone: Phone number with validation (optional)
    - birth_date: Date of birth (optional)
    - bio: Short biography or description (optional)
    - created_at: Timestamp when profile was created
    - updated_at: Timestamp when profile was last updated
    """
    
    # Phone number validator for international format
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. "
                "Up to 15 digits allowed."
    )
    
    # One-to-one relationship with User model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text='Associated user account for this profile'
    )
    
    # Personal information fields
    first_name = models.CharField(
        'First Name',
        max_length=30,
        blank=True,
        help_text='User\'s first name'
    )
    
    last_name = models.CharField(
        'Last Name', 
        max_length=30,
        blank=True,
        help_text='User\'s last name'
    )
    
    phone = models.CharField(
        'Phone Number',
        max_length=17,  # +999999999999999
        blank=True,
        validators=[phone_validator],
        help_text='Phone number in international format (e.g., +1234567890)'
    )
    
    birth_date = models.DateField(
        'Birth Date',
        blank=True,
        null=True,
        help_text='User\'s date of birth'
    )
    
    bio = models.TextField(
        'Biography',
        max_length=500,
        blank=True,
        help_text='Short biography or description (max 500 characters)'
    )
    
    # Timestamp fields for audit trail
    created_at = models.DateTimeField(
        'Created At',
        auto_now_add=True,
        help_text='Timestamp when the profile was created'
    )
    
    updated_at = models.DateTimeField(
        'Updated At',
        auto_now=True,
        help_text='Timestamp when the profile was last updated'
    )
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        db_table = 'profiles_profile'
        ordering = ['-created_at']  # Most recent first
        
    def __str__(self):
        """Return string representation of the profile."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return f"Profile for {self.user.username}"
    
    def clean(self):
        """
        Model-level validation.
        
        Validates that birth_date is not in the future and other business rules.
        """
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        super().clean()
        
        # Validate birth_date is not in the future
        if self.birth_date and self.birth_date > timezone.now().date():
            raise ValidationError({
                'birth_date': 'Birth date cannot be in the future.'
            })
    
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        Falls back to username if no names are provided.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.user.username
    
    def get_short_name(self):
        """
        Return the short name for the user.
        Falls back to username if no first name is provided.
        """
        return self.first_name or self.user.username
    
    @property
    def age(self):
        """
        Calculate and return the user's age based on birth_date.
        Returns None if birth_date is not set.
        """
        if not self.birth_date:
            return None
            
        from django.utils import timezone
        today = timezone.now().date()
        age = today.year - self.birth_date.year
        
        # Adjust if birthday hasn't occurred this year
        if today.month < self.birth_date.month or (
            today.month == self.birth_date.month and today.day < self.birth_date.day
        ):
            age -= 1
            
        return age
