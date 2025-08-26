from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from categories.models import Category

User = get_user_model()


class Command(BaseCommand):
    help = 'Create default categories for users who don\'t have any categories yet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-email',
            type=str,
            help='Email of specific user to seed categories for',
        )
        parser.add_argument(
            '--all-users',
            action='store_true',
            help='Seed categories for all users who don\'t have any',
        )

    def handle(self, *args, **options):
        if options['user_email']:
            try:
                user = User.objects.get(email=options['user_email'])
                self.seed_user_categories(user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with email {options["user_email"]} not found')
                )
        elif options['all_users']:
            users_without_categories = User.objects.exclude(
                categories__isnull=False
            ).distinct()
            
            if not users_without_categories.exists():
                self.stdout.write(
                    self.style.WARNING('All users already have categories')
                )
                return
                
            for user in users_without_categories:
                self.seed_user_categories(user)
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Please specify --user-email=<email> or --all-users'
                )
            )

    def seed_user_categories(self, user):
        """Create default categories for a user."""
        self.stdout.write(f'Creating default categories for {user.email}...')
        
        # Default expense categories
        expense_categories = [
            # Main categories
            {'name': 'Food & Dining', 'icon': '🍔', 'color': '#10B981', 'children': [
                'Restaurants',
                'Groceries', 
                'Fast Food',
                'Coffee Shops'
            ]},
            {'name': 'Transportation', 'icon': '🚗', 'color': '#3B82F6', 'children': [
                'Gas',
                'Public Transport',
                'Parking',
                'Car Maintenance'
            ]},
            {'name': 'Housing', 'icon': '🏠', 'color': '#8B5CF6', 'children': [
                'Rent/Mortgage',
                'Utilities',
                'Internet',
                'Home Maintenance'
            ]},
            {'name': 'Entertainment', 'icon': '🎬', 'color': '#F59E0B', 'children': [
                'Movies',
                'Streaming Services',
                'Games',
                'Events'
            ]},
            {'name': 'Healthcare', 'icon': '🏥', 'color': '#EF4444', 'children': [
                'Doctor Visits',
                'Pharmacy',
                'Insurance',
                'Dental'
            ]},
            {'name': 'Shopping', 'icon': '🛍️', 'color': '#06B6D4', 'children': [
                'Clothing',
                'Electronics',
                'Personal Care',
                'Gifts'
            ]},
            {'name': 'Education', 'icon': '🎓', 'color': '#84CC16'},
            {'name': 'Travel', 'icon': '✈️', 'color': '#F97316'},
            {'name': 'Other Expenses', 'icon': '💰', 'color': '#6B7280'},
        ]
        
        # Default income categories
        income_categories = [
            {'name': 'Salary', 'icon': '💰', 'color': '#10B981', 'children': [
                'Primary Job',
                'Bonus',
                'Overtime'
            ]},
            {'name': 'Freelance', 'icon': '👔', 'color': '#3B82F6'},
            {'name': 'Investments', 'icon': '📊', 'color': '#8B5CF6', 'children': [
                'Dividends',
                'Interest',
                'Capital Gains'
            ]},
            {'name': 'Other Income', 'icon': '🎁', 'color': '#84CC16'},
        ]
        
        created_count = 0
        
        # Create expense categories
        for category_data in expense_categories:
            parent_category = Category.objects.create(
                user=user,
                name=category_data['name'],
                category_type='EXPENSE',
                icon=category_data['icon'],
                color=category_data['color']
            )
            created_count += 1
            
            # Create child categories if any
            for child_name in category_data.get('children', []):
                Category.objects.create(
                    user=user,
                    name=child_name,
                    category_type='EXPENSE',
                    parent=parent_category,
                    icon=category_data['icon'],  # Use same icon as parent
                    color=category_data['color']  # Use same color as parent
                )
                created_count += 1
        
        # Create income categories
        for category_data in income_categories:
            parent_category = Category.objects.create(
                user=user,
                name=category_data['name'],
                category_type='INCOME',
                icon=category_data['icon'],
                color=category_data['color']
            )
            created_count += 1
            
            # Create child categories if any
            for child_name in category_data.get('children', []):
                Category.objects.create(
                    user=user,
                    name=child_name,
                    category_type='INCOME',
                    parent=parent_category,
                    icon=category_data['icon'],  # Use same icon as parent
                    color=category_data['color']  # Use same color as parent
                )
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} categories for {user.email}'
            )
        )