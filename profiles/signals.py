from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile


User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically create a Profile when a User is created.
    
    This signal ensures that every User has an associated Profile object,
    maintaining the one-to-one relationship integrity and providing a
    seamless user experience where profiles are always available.
    
    Args:
        sender: The User model class
        instance: The User instance that was saved
        created: Boolean indicating if this is a new User
        **kwargs: Additional keyword arguments from the signal
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the User's Profile when the User is saved.
    
    This ensures that the Profile is kept in sync with any User changes
    that might affect the profile relationship. If for some reason the
    profile doesn't exist, it creates one.
    
    Args:
        sender: The User model class
        instance: The User instance that was saved
        **kwargs: Additional keyword arguments from the signal
    """
    # Check if profile exists, create if it doesn't
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()