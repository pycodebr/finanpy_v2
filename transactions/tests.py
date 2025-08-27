from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta

from .models import Transaction
from accounts.models import Account
from categories.models import Category

User = get_user_model()


class TransactionModelTest(TestCase):
    """Test cases for the Transaction model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        
        self.account = Account.objects.create(
            user=self.user,
            name='Test Checking Account',
            account_type='checking',
            balance=Decimal('1000.00'),
            currency='BRL'
        )
        
        self.expense_category = Category.objects.create(
            user=self.user,
            name='Food',
            category_type='EXPENSE',
            color='#EF4444',
            icon='🍔'
        )
        
        self.income_category = Category.objects.create(
            user=self.user,
            name='Salary',
            category_type='INCOME',
            color='#10B981',
            icon='💰'
        )
    
    def test_create_valid_expense_transaction(self):
        """Test creating a valid expense transaction."""
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=Decimal('50.00'),
            description='Lunch at restaurant',
            transaction_date=date.today()
        )
        
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.account, self.account)
        self.assertEqual(transaction.category, self.expense_category)
        self.assertEqual(transaction.transaction_type, 'EXPENSE')
        self.assertEqual(transaction.amount, Decimal('50.00'))
        self.assertEqual(transaction.description, 'Lunch at restaurant')
        self.assertFalse(transaction.is_recurring)
        self.assertIsNone(transaction.recurrence_type)
    
    def test_create_valid_income_transaction(self):
        """Test creating a valid income transaction."""
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.income_category,
            transaction_type='INCOME',
            amount=Decimal('2500.00'),
            description='Monthly salary',
            transaction_date=date.today(),
            is_recurring=True,
            recurrence_type='MONTHLY'
        )
        
        self.assertEqual(transaction.transaction_type, 'INCOME')
        self.assertTrue(transaction.is_recurring)
        self.assertEqual(transaction.recurrence_type, 'MONTHLY')
    
    def test_transaction_str_representation(self):
        """Test the string representation of transaction."""
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=Decimal('25.50'),
            description='Coffee',
            transaction_date=date.today()
        )
        
        expected_str = f"- 25.50 - Coffee ({date.today()})"
        self.assertEqual(str(transaction), expected_str)
    
    def test_amount_validation(self):
        """Test that amount must be positive."""
        with self.assertRaises(ValidationError):
            transaction = Transaction(
                user=self.user,
                account=self.account,
                category=self.expense_category,
                transaction_type='EXPENSE',
                amount=Decimal('0.00'),
                description='Invalid amount',
                transaction_date=date.today()
            )
            transaction.full_clean()
    
    def test_future_date_validation(self):
        """Test that transaction date cannot be in the future."""
        with self.assertRaises(ValidationError):
            transaction = Transaction(
                user=self.user,
                account=self.account,
                category=self.expense_category,
                transaction_type='EXPENSE',
                amount=Decimal('100.00'),
                description='Future transaction',
                transaction_date=date.today() + timedelta(days=1)
            )
            transaction.full_clean()
    
    def test_category_type_validation(self):
        """Test that category type must match transaction type."""
        with self.assertRaises(ValidationError):
            transaction = Transaction(
                user=self.user,
                account=self.account,
                category=self.income_category,  # Income category
                transaction_type='EXPENSE',     # Expense transaction
                amount=Decimal('100.00'),
                description='Mismatched types',
                transaction_date=date.today()
            )
            transaction.full_clean()
    
    def test_user_data_isolation(self):
        """Test that users can only use their own accounts and categories."""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='pass123'
        )
        
        with self.assertRaises(ValidationError):
            transaction = Transaction(
                user=other_user,
                account=self.account,  # Account belongs to different user
                category=self.expense_category,
                transaction_type='EXPENSE',
                amount=Decimal('100.00'),
                description='Cross-user transaction',
                transaction_date=date.today()
            )
            transaction.full_clean()
    
    def test_recurring_transaction_validation(self):
        """Test validation of recurring transaction fields."""
        # Test that recurring transactions need recurrence_type
        with self.assertRaises(ValidationError):
            transaction = Transaction(
                user=self.user,
                account=self.account,
                category=self.expense_category,
                transaction_type='EXPENSE',
                amount=Decimal('100.00'),
                description='Recurring without type',
                transaction_date=date.today(),
                is_recurring=True
                # Missing recurrence_type
            )
            transaction.full_clean()
        
        # Test that non-recurring transactions shouldn't have recurrence_type
        with self.assertRaises(ValidationError):
            transaction = Transaction(
                user=self.user,
                account=self.account,
                category=self.expense_category,
                transaction_type='EXPENSE',
                amount=Decimal('100.00'),
                description='Non-recurring with type',
                transaction_date=date.today(),
                is_recurring=False,
                recurrence_type='MONTHLY'  # Should not be set
            )
            transaction.full_clean()
    
    def test_amount_display_property(self):
        """Test the amount_display property formatting."""
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=Decimal('1234.56'),
            description='Display test',
            transaction_date=date.today()
        )
        
        # Brazilian format: R$ 1.234,56
        self.assertEqual(transaction.amount_display, 'R$ 1.234,56')
    
    def test_amount_with_sign_property(self):
        """Test the amount_with_sign property."""
        expense = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=Decimal('100.00'),
            description='Expense test',
            transaction_date=date.today()
        )
        
        income = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.income_category,
            transaction_type='INCOME',
            amount=Decimal('200.00'),
            description='Income test',
            transaction_date=date.today()
        )
        
        self.assertEqual(expense.amount_with_sign, Decimal('-100.00'))
        self.assertEqual(income.amount_with_sign, Decimal('200.00'))
    
    def test_get_monthly_summary_classmethod(self):
        """Test the get_monthly_summary class method."""
        # Create test transactions
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.income_category,
            transaction_type='INCOME',
            amount=Decimal('2000.00'),
            description='Salary',
            transaction_date=date.today()
        )
        
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=Decimal('500.00'),
            description='Groceries',
            transaction_date=date.today()
        )
        
        summary = Transaction.get_monthly_summary(
            self.user, 
            date.today().year, 
            date.today().month
        )
        
        self.assertEqual(summary['income'], Decimal('2000.00'))
        self.assertEqual(summary['expenses'], Decimal('500.00'))
        self.assertEqual(summary['balance'], Decimal('1500.00'))
        self.assertEqual(summary['transaction_count'], 2)


class TransactionSignalsTest(TestCase):
    """Test cases for transaction signals and automatic balance updates."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='signaltest@example.com',
            password='testpass123'
        )
        
        self.account = Account.objects.create(
            user=self.user,
            name='Signal Test Account',
            account_type='checking',
            balance=Decimal('0.00'),  # Start with 0 balance to simplify validation
            currency='BRL'
        )
        
        self.expense_category = Category.objects.create(
            user=self.user,
            name='Test Expenses',
            category_type='EXPENSE',
            color='#EF4444',
            icon='🍔'  # Valid icon from ICON_CHOICES
        )
        
        self.income_category = Category.objects.create(
            user=self.user,
            name='Test Income',
            category_type='INCOME',
            color='#10B981',
            icon='💰'  # Valid icon from ICON_CHOICES
        )
    
    def test_account_balance_increases_on_income_transaction(self):
        """Test that account balance increases when income transaction is created."""
        initial_balance = self.account.balance
        transaction_amount = Decimal('200.00')
        
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.income_category,
            transaction_type='INCOME',
            amount=transaction_amount,
            description='Test income',
            transaction_date=date.today()
        )
        
        # Refresh account from database to get updated balance
        self.account.refresh_from_db()
        
        expected_balance = initial_balance + transaction_amount
        self.assertEqual(self.account.balance, expected_balance)
    
    def test_account_balance_decreases_on_expense_transaction(self):
        """Test that account balance decreases when expense transaction is created."""
        initial_balance = self.account.balance
        transaction_amount = Decimal('75.50')
        
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=transaction_amount,
            description='Test expense',
            transaction_date=date.today()
        )
        
        # Refresh account from database to get updated balance
        self.account.refresh_from_db()
        
        expected_balance = initial_balance - transaction_amount
        self.assertEqual(self.account.balance, expected_balance)
    
    def test_account_balance_updates_on_transaction_amount_change(self):
        """Test that account balance updates correctly when transaction amount is changed."""
        initial_balance = self.account.balance
        original_amount = Decimal('100.00')
        new_amount = Decimal('150.00')
        
        # Create transaction
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=original_amount,
            description='Test expense update',
            transaction_date=date.today()
        )
        
        # Check balance after creation
        self.account.refresh_from_db()
        balance_after_create = initial_balance - original_amount
        self.assertEqual(self.account.balance, balance_after_create)
        
        # Update transaction amount
        transaction.amount = new_amount
        transaction.save()
        
        # Check balance after update
        self.account.refresh_from_db()
        expected_balance = initial_balance - new_amount
        self.assertEqual(self.account.balance, expected_balance)
    
    def test_account_balance_updates_on_transaction_type_change(self):
        """Test that account balance updates correctly when transaction type is changed."""
        initial_balance = self.account.balance
        transaction_amount = Decimal('100.00')
        
        # Create expense transaction
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=transaction_amount,
            description='Test type change',
            transaction_date=date.today()
        )
        
        # Check balance after expense creation
        self.account.refresh_from_db()
        balance_after_expense = initial_balance - transaction_amount
        self.assertEqual(self.account.balance, balance_after_expense)
        
        # Change to income transaction (also need to change category)
        transaction.transaction_type = 'INCOME'
        transaction.category = self.income_category
        transaction.save()
        
        # Check balance after changing to income
        self.account.refresh_from_db()
        expected_balance = initial_balance + transaction_amount
        self.assertEqual(self.account.balance, expected_balance)
    
    def test_account_balance_reverts_on_transaction_deletion(self):
        """Test that account balance reverts when transaction is deleted."""
        initial_balance = self.account.balance
        transaction_amount = Decimal('80.00')
        
        # Create transaction
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=transaction_amount,
            description='Test deletion',
            transaction_date=date.today()
        )
        
        # Check balance after creation
        self.account.refresh_from_db()
        balance_after_create = initial_balance - transaction_amount
        self.assertEqual(self.account.balance, balance_after_create)
        
        # Delete transaction
        transaction.delete()
        
        # Check balance reverts to initial
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, initial_balance)
    
    def test_multiple_transactions_balance_calculation(self):
        """Test correct balance calculation with multiple transactions."""
        initial_balance = self.account.balance
        
        # Create multiple transactions
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.income_category,
            transaction_type='INCOME',
            amount=Decimal('300.00'),
            description='Income 1',
            transaction_date=date.today()
        )
        
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=Decimal('150.00'),
            description='Expense 1',
            transaction_date=date.today()
        )
        
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.income_category,
            transaction_type='INCOME',
            amount=Decimal('100.00'),
            description='Income 2',
            transaction_date=date.today()
        )
        
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=Decimal('75.00'),
            description='Expense 2',
            transaction_date=date.today()
        )
        
        # Check final balance
        self.account.refresh_from_db()
        expected_balance = (
            initial_balance + 
            Decimal('300.00') + Decimal('100.00') -  # Incomes
            Decimal('150.00') - Decimal('75.00')     # Expenses
        )  # = 500.00 + 400.00 - 225.00 = 675.00
        self.assertEqual(self.account.balance, expected_balance)
    
    def test_account_balance_with_different_accounts(self):
        """Test that transactions only affect their respective accounts."""
        # Create second account
        account2 = Account.objects.create(
            user=self.user,
            name='Second Account',
            account_type='savings',
            balance=Decimal('200.00'),
            currency='BRL'
        )
        
        initial_balance1 = self.account.balance
        initial_balance2 = account2.balance
        
        # Create transaction on first account
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=Decimal('50.00'),
            description='First account expense',
            transaction_date=date.today()
        )
        
        # Create transaction on second account
        Transaction.objects.create(
            user=self.user,
            account=account2,
            category=self.income_category,
            transaction_type='INCOME',
            amount=Decimal('100.00'),
            description='Second account income',
            transaction_date=date.today()
        )
        
        # Refresh both accounts
        self.account.refresh_from_db()
        account2.refresh_from_db()
        
        # Check balances are updated independently
        self.assertEqual(self.account.balance, initial_balance1 - Decimal('50.00'))
        self.assertEqual(account2.balance, initial_balance2 + Decimal('100.00'))
        
    def test_balance_consistency_with_signal_utility_functions(self):
        """Test balance consistency using signal utility functions."""
        from transactions.signals import validate_account_balances, recalculate_account_balance
        
        initial_balance = self.account.balance
        
        # Create some transactions
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.income_category,
            transaction_type='INCOME',
            amount=Decimal('1000.00'),
            description='Large income',
            transaction_date=date.today()
        )
        
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            transaction_type='EXPENSE',
            amount=Decimal('250.00'),
            description='Large expense',
            transaction_date=date.today()
        )
        
        # Validate balances - should return no discrepancies
        discrepancies = validate_account_balances(user=self.user)
        self.assertEqual(len(discrepancies), 0)
        
        # Manually corrupt balance to test recalculation
        self.account.balance = Decimal('999999.99')
        self.account.save(update_fields=['balance'])
        
        # Validate should now find discrepancy
        discrepancies = validate_account_balances(user=self.user)
        self.assertEqual(len(discrepancies), 1)
        
        # Recalculate balance
        old_balance, new_balance, difference = recalculate_account_balance(self.account)
        
        # Check that balance was corrected 
        # Since initial_balance is now 0.00, expected is just the transaction impact
        expected_balance = Decimal('1000.00') - Decimal('250.00')  # 750.00
        self.assertEqual(new_balance, expected_balance)
        
        # Validate again - should be clean now
        discrepancies = validate_account_balances(user=self.user)
        self.assertEqual(len(discrepancies), 0)
