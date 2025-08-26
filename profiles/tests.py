from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.utils import timezone

from .models import Profile

User = get_user_model()


class ProfileModelTest(TestCase):
    """Test cases for the Profile model."""
    
    def setUp(self):
        """Set up test user for profile tests."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_creation(self):
        """Test basic profile creation."""
        # Since profile is automatically created, we'll update the existing one
        profile = self.user.profile
        profile.first_name = 'John'
        profile.last_name = 'Doe'
        profile.phone = '+1234567890'
        profile.birth_date = date(1990, 5, 15)
        profile.bio = 'Test biography'
        profile.save()
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.first_name, 'John')
        self.assertEqual(profile.last_name, 'Doe')
        self.assertEqual(profile.phone, '+1234567890')
        self.assertEqual(profile.birth_date, date(1990, 5, 15))
        self.assertEqual(profile.bio, 'Test biography')
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
    
    def test_profile_str_method(self):
        """Test Profile __str__ method."""
        # Use the automatically created profile and update it
        profile = self.user.profile
        profile.first_name = 'John'
        profile.last_name = 'Doe'
        profile.save()
        self.assertEqual(str(profile), 'John Doe')
        
        # Test with only first name
        profile.last_name = ''
        profile.save()
        self.assertEqual(str(profile), 'John')
        
        # Test with no names
        profile.first_name = ''
        profile.save()
        self.assertEqual(str(profile), f'Profile for {self.user.username}')
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        profile = self.user.profile
        
        # Test with both names
        profile.first_name = 'John'
        profile.last_name = 'Doe'
        self.assertEqual(profile.get_full_name(), 'John Doe')
        
        # Test with only first name
        profile.last_name = ''
        self.assertEqual(profile.get_full_name(), 'John')
        
        # Test with only last name
        profile.first_name = ''
        profile.last_name = 'Doe'
        self.assertEqual(profile.get_full_name(), 'Doe')
        
        # Test with no names
        profile.last_name = ''
        self.assertEqual(profile.get_full_name(), self.user.username)
    
    def test_get_short_name(self):
        """Test get_short_name method."""
        profile = self.user.profile
        profile.first_name = 'John'
        profile.save()
        self.assertEqual(profile.get_short_name(), 'John')
        
        # Test without first name
        profile.first_name = ''
        profile.save()
        self.assertEqual(profile.get_short_name(), self.user.username)
    
    def test_age_property(self):
        """Test age calculation property."""
        # Test with birth date
        birth_date = date(1990, 1, 1)
        profile = self.user.profile
        profile.birth_date = birth_date
        profile.save()
        
        expected_age = timezone.now().date().year - 1990
        # Adjust for birthday not yet occurred this year
        if timezone.now().date().month < 1 or (
            timezone.now().date().month == 1 and timezone.now().date().day < 1
        ):
            expected_age -= 1
            
        self.assertEqual(profile.age, expected_age)
        
        # Test without birth date
        profile.birth_date = None
        profile.save()
        self.assertIsNone(profile.age)
    
    def test_phone_validation(self):
        """Test phone number validation."""
        # Valid phone numbers - test with the automatically created profile
        valid_phones = ['+1234567890', '1234567890', '+123456789012345']
        
        profile = self.user.profile
        for phone in valid_phones:
            profile.phone = phone
            try:
                profile.full_clean()
            except ValidationError:
                self.fail(f'Valid phone number {phone} failed validation')
        
        # Invalid phone numbers
        invalid_phones = ['123', 'abc', '+12345678901234567890']  # Too short, letters, too long
        
        for phone in invalid_phones:
            profile.phone = phone
            with self.assertRaises(ValidationError):
                profile.full_clean()
    
    def test_birth_date_validation(self):
        """Test birth date validation."""
        profile = self.user.profile
        
        # Future date should be invalid
        future_date = timezone.now().date() + timedelta(days=1)
        profile.birth_date = future_date
        
        with self.assertRaises(ValidationError):
            profile.full_clean()
        
        # Past date should be valid
        past_date = date(1990, 1, 1)
        profile.birth_date = past_date
        try:
            profile.full_clean()
        except ValidationError:
            self.fail('Valid past birth date failed validation')
    
    def test_one_to_one_relationship(self):
        """Test OneToOne relationship with User."""
        profile = self.user.profile
        
        # Test forward relationship
        self.assertEqual(profile.user, self.user)
        
        # Test reverse relationship
        self.assertEqual(self.user.profile, profile)
        
        # Test that creating another profile for same user raises error
        with self.assertRaises(Exception):  # IntegrityError
            Profile.objects.create(user=self.user)


class ProfileSignalTest(TestCase):
    """Test cases for Profile creation signals."""
    
    def test_profile_created_automatically_on_user_creation(self):
        """Test that a Profile is automatically created when a User is created."""
        # Create a new user
        user = User.objects.create_user(
            username='signaluser',
            email='signal@example.com',
            password='testpass123'
        )
        
        # Check that a profile was automatically created
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)
        self.assertEqual(user.profile.user, user)
        
        # Verify the profile has default values
        self.assertEqual(user.profile.first_name, '')
        self.assertEqual(user.profile.last_name, '')
        self.assertEqual(user.profile.phone, '')
        self.assertIsNone(user.profile.birth_date)
        self.assertEqual(user.profile.bio, '')
        self.assertIsNotNone(user.profile.created_at)
        self.assertIsNotNone(user.profile.updated_at)
    
    def test_profile_created_for_superuser(self):
        """Test that a Profile is automatically created for superusers."""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Check that a profile was automatically created for superuser
        self.assertTrue(hasattr(superuser, 'profile'))
        self.assertIsInstance(superuser.profile, Profile)
        self.assertEqual(superuser.profile.user, superuser)
    
    def test_profile_not_duplicated_on_user_save(self):
        """Test that saving an existing user doesn't create duplicate profiles."""
        # Create a new user (profile should be created automatically)
        user = User.objects.create_user(
            username='saveuser',
            email='save@example.com',
            password='testpass123'
        )
        
        # Get the original profile
        original_profile = user.profile
        original_profile_id = original_profile.id
        
        # Modify and save the user
        user.email = 'newsave@example.com'
        user.save()
        
        # Refresh from database
        user.refresh_from_db()
        
        # Check that the same profile still exists (not duplicated)
        self.assertEqual(user.profile.id, original_profile_id)
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)
    
    def test_profile_created_if_missing_on_user_save(self):
        """Test that a Profile is created if somehow missing when User is saved."""
        # Create a user
        user = User.objects.create_user(
            username='missingprofile',
            email='missing@example.com',
            password='testpass123'
        )
        
        # Delete the profile (simulating a corrupted state)
        user.profile.delete()
        
        # Verify profile is gone by checking the database directly
        self.assertFalse(Profile.objects.filter(user=user).exists())
        
        # Save the user - this should trigger signal to recreate profile
        user.save()
        
        # Refresh from database and check profile exists again
        user.refresh_from_db()
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertIsInstance(user.profile, Profile)
        self.assertEqual(user.profile.user, user)
    
    def test_multiple_users_get_individual_profiles(self):
        """Test that multiple users each get their own individual profiles."""
        # Create multiple users
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='testpass123'
        )
        
        # Check that each user has their own profile
        self.assertTrue(hasattr(user1, 'profile'))
        self.assertTrue(hasattr(user2, 'profile'))
        self.assertTrue(hasattr(user3, 'profile'))
        
        # Verify profiles are different objects
        self.assertNotEqual(user1.profile.id, user2.profile.id)
        self.assertNotEqual(user1.profile.id, user3.profile.id)
        self.assertNotEqual(user2.profile.id, user3.profile.id)
        
        # Verify each profile belongs to the correct user
        self.assertEqual(user1.profile.user, user1)
        self.assertEqual(user2.profile.user, user2)
        self.assertEqual(user3.profile.user, user3)
