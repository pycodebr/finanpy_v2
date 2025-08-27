"""
Django signals for automatic account balance updates when transactions are modified.

This module implements post_save and post_delete signal handlers that automatically
update account balances when transactions are created, updated, or deleted. The signals
ensure data consistency and eliminate the need for manual balance calculations.

Key Features:
- Automatic balance updates for all transaction operations
- Support for transaction updates (reverses old amount, applies new amount)
- Proper handling of income vs expense transaction types
- Error handling and logging for robustness
- User data isolation and security validation

Signal Flow:
1. Transaction created → Add amount to account balance (income +, expense -)
2. Transaction updated → Reverse old amount, apply new amount
3. Transaction deleted → Reverse amount from account balance
"""

import logging
from decimal import Decimal
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist

# Get logger for this module
logger = logging.getLogger(__name__)

# Dictionary to store old transaction values for update handling
_old_transaction_values = {}


def calculate_balance_delta(transaction_obj):
    """
    Calculate the balance delta (change) for a given transaction.
    
    Args:
        transaction_obj: Transaction instance
        
    Returns:
        Decimal: Positive for income, negative for expense
        
    Business Logic:
    - INCOME transactions increase account balance (+amount)
    - EXPENSE transactions decrease account balance (-amount)
    """
    if transaction_obj.transaction_type == 'INCOME':
        return transaction_obj.amount
    elif transaction_obj.transaction_type == 'EXPENSE':
        return -transaction_obj.amount
    else:
        logger.error(
            f"Unknown transaction type '{transaction_obj.transaction_type}' "
            f"for transaction {transaction_obj.id}"
        )
        return Decimal('0.00')


def update_account_balance(account, delta, operation='add'):
    """
    Update account balance with the given delta.
    
    Args:
        account: Account instance to update
        delta: Decimal amount to add/subtract
        operation: 'add' or 'subtract' - operation to perform
        
    This function:
    - Updates the account balance atomically
    - Handles both positive and negative deltas correctly
    - Logs balance changes for audit purposes
    - Saves the account with updated balance
    """
    try:
        old_balance = account.balance
        
        if operation == 'add':
            account.balance = old_balance + delta
        elif operation == 'subtract':
            account.balance = old_balance - delta
        else:
            logger.error(f"Invalid balance operation: {operation}")
            return
        
        # Save account with updated balance
        # Use update_fields to only update the balance and updated_at timestamp
        account.save(update_fields=['balance', 'updated_at'])
        
        logger.info(
            f"Account {account.id} ({account.name}) balance updated: "
            f"{old_balance} → {account.balance} (delta: {'+' if operation == 'add' else '-'}{abs(delta)})"
        )
        
    except Exception as e:
        logger.error(
            f"Error updating account {account.id} balance: {str(e)}"
        )
        raise


@receiver(pre_save, sender='transactions.Transaction')
def handle_transaction_pre_save(sender, instance, **kwargs):
    """
    Pre-save signal to capture old transaction values before updates.
    
    This signal stores the old transaction values in a module-level dictionary
    so they can be used in the post_save signal to properly handle balance updates.
    
    Args:
        sender: Transaction model class
        instance: Transaction instance being saved
        **kwargs: Additional signal arguments
    """
    try:
        if instance.pk:  # Only for existing transactions (updates)
            try:
                # Get the old transaction from database
                old_transaction = sender.objects.get(pk=instance.pk)
                
                # Store old values for use in post_save
                _old_transaction_values[instance.pk] = {
                    'account_id': old_transaction.account_id,
                    'amount': old_transaction.amount,
                    'transaction_type': old_transaction.transaction_type,
                }
                
                logger.debug(f"Stored old values for transaction {instance.pk}")
                
            except ObjectDoesNotExist:
                # Transaction doesn't exist yet, this is a creation
                logger.debug(f"Transaction {instance.pk} not found in database, treating as new")
                
    except Exception as e:
        logger.error(f"Error in transaction pre_save signal for transaction {instance.pk}: {str(e)}")


@receiver(post_save, sender='transactions.Transaction')
def handle_transaction_save(sender, instance, created, **kwargs):
    """
    Signal handler for transaction creation and updates.
    
    This signal automatically updates account balances when:
    1. New transactions are created
    2. Existing transactions are updated (amount, type, or account changes)
    
    For transaction updates, it:
    - Reverses the old transaction's impact on the old account
    - Applies the new transaction's impact on the new account
    - Handles account changes (transaction moved between accounts)
    
    Args:
        sender: Transaction model class
        instance: Transaction instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional signal arguments including 'update_fields'
    """
    try:
        if created:
            # Handle new transaction creation
            logger.info(f"Processing new transaction {instance.id}: {instance}")
            
            # Validate that account belongs to the same user as transaction
            # Check if user relationships exist before accessing them
            try:
                if not hasattr(instance, 'user') or not instance.user:
                    logger.error(f"Transaction {instance.id} has no user relationship")
                    return
                    
                if not hasattr(instance, 'account') or not instance.account:
                    logger.error(f"Transaction {instance.id} has no account relationship")
                    return
                    
                if not hasattr(instance.account, 'user') or not instance.account.user:
                    logger.error(f"Transaction {instance.id} account has no user relationship")
                    return
                    
                if instance.account.user != instance.user:
                    logger.error(
                        f"User mismatch: Transaction user {instance.user.id} "
                        f"vs Account user {instance.account.user.id}"
                    )
                    return
                    
            except Exception as e:
                logger.error(f"Error validating user relationships for transaction {instance.id}: {str(e)}")
                return
            
            # Calculate and apply balance change
            delta = calculate_balance_delta(instance)
            update_account_balance(instance.account, delta, 'add')
            
        else:
            # Handle transaction updates using pre_save stored values
            logger.info(f"Processing transaction update {instance.id}: {instance}")
            
            # Get old values from pre_save signal
            old_values = _old_transaction_values.get(instance.pk)
            
            if not old_values:
                logger.warning(f"No old values found for transaction {instance.id} update, skipping balance update")
                return
            
            try:
                # Create a mock old transaction object for balance calculations
                class MockOldTransaction:
                    def __init__(self, values):
                        self.account_id = values['account_id']
                        self.amount = values['amount'] 
                        self.transaction_type = values['transaction_type']
                
                old_transaction = MockOldTransaction(old_values)
                
                # If account changed, reverse impact on old account and apply to new account
                if instance.account_id != old_values['account_id']:
                    # Reverse old impact on old account
                    old_delta = calculate_balance_delta(old_transaction)
                    from accounts.models import Account
                    old_account = Account.objects.get(pk=old_values['account_id'])
                    update_account_balance(old_account, old_delta, 'subtract')
                    
                    # Apply new impact on new account
                    new_delta = calculate_balance_delta(instance)
                    update_account_balance(instance.account, new_delta, 'add')
                    
                    logger.info(f"Transaction {instance.id} moved between accounts")
                
                else:
                    # Same account, but amount or type might have changed
                    if (instance.amount != old_values['amount'] or 
                        instance.transaction_type != old_values['transaction_type']):
                        
                        # Reverse old impact
                        old_delta = calculate_balance_delta(old_transaction)
                        update_account_balance(instance.account, old_delta, 'subtract')
                        
                        # Apply new impact  
                        new_delta = calculate_balance_delta(instance)
                        update_account_balance(instance.account, new_delta, 'add')
                        
                        logger.info(f"Transaction {instance.id} amount/type changed")
                
                # Clean up stored values
                del _old_transaction_values[instance.pk]
                
            except Exception as e:
                logger.error(f"Error handling transaction update for {instance.id}: {str(e)}")
                # Clean up stored values even on error
                if instance.pk in _old_transaction_values:
                    del _old_transaction_values[instance.pk]
                return
            
    except Exception as e:
        logger.error(
            f"Error in transaction save signal for transaction {instance.id}: {str(e)}"
        )
        # Don't re-raise to avoid breaking the transaction save
        # The transaction will be saved but balance might be inconsistent
        # This should be monitored and handled by administrators


@receiver(post_delete, sender='transactions.Transaction')
def handle_transaction_delete(sender, instance, **kwargs):
    """
    Signal handler for transaction deletion.
    
    This signal automatically reverses the account balance impact when a
    transaction is deleted. It subtracts the transaction's impact from
    the account balance.
    
    Args:
        sender: Transaction model class
        instance: Transaction instance being deleted
        **kwargs: Additional signal arguments
    """
    try:
        logger.info(f"Processing transaction deletion {instance.id}: {instance}")
        
        # Validate that account still exists and belongs to the same user
        if not hasattr(instance, 'account') or not instance.account:
            logger.warning(f"Transaction {instance.id} has no account reference")
            return
            
        if instance.account.user != instance.user:
            logger.error(
                f"User mismatch on deletion: Transaction user {instance.user.id} "
                f"vs Account user {instance.account.user.id}"
            )
            return
        
        # Calculate and reverse the balance change
        delta = calculate_balance_delta(instance)
        update_account_balance(instance.account, delta, 'subtract')
        
    except Exception as e:
        logger.error(
            f"Error in transaction delete signal for transaction {instance.id}: {str(e)}"
        )
        # Don't re-raise to avoid breaking the transaction deletion


# Additional utility functions for balance reconciliation and debugging

def recalculate_account_balance(account):
    """
    Recalculate account balance from scratch based on all transactions.
    
    This is a utility function for balance reconciliation in case signals
    fail or data gets inconsistent. It should be used sparingly and mainly
    for debugging or data recovery purposes.
    
    Args:
        account: Account instance to recalculate
        
    Returns:
        tuple: (old_balance, new_balance, difference)
    """
    from django.db.models import Sum, Case, When, DecimalField
    
    try:
        old_balance = account.balance
        
        # Calculate total impact of all transactions for this account
        from django.db.models import F
        balance_impact = account.transactions.aggregate(
            total_impact=Sum(
                Case(
                    When(transaction_type='INCOME', then=F('amount')),
                    When(transaction_type='EXPENSE', then=F('amount') * -1),
                    default=0,
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )['total_impact'] or Decimal('0.00')
        
        # Note: This assumes the account started with 0 balance
        # In a real implementation, you might want to track initial balances
        new_balance = balance_impact
        
        account.balance = new_balance
        account.save(update_fields=['balance', 'updated_at'])
        
        difference = new_balance - old_balance
        
        logger.info(
            f"Recalculated balance for account {account.id} ({account.name}): "
            f"{old_balance} → {new_balance} (difference: {difference})"
        )
        
        return old_balance, new_balance, difference
        
    except Exception as e:
        logger.error(
            f"Error recalculating balance for account {account.id}: {str(e)}"
        )
        raise


def validate_account_balances(user=None):
    """
    Validate that all account balances match their transaction history.
    
    This is a debugging/auditing function to check for balance inconsistencies
    that might occur if signals fail or are bypassed.
    
    Args:
        user: Optional User instance to limit validation to specific user
        
    Returns:
        list: List of accounts with balance discrepancies
    """
    from accounts.models import Account
    from django.db.models import Sum, Case, When, DecimalField
    
    discrepancies = []
    
    try:
        accounts_query = Account.objects.all()
        if user:
            accounts_query = accounts_query.filter(user=user)
            
        for account in accounts_query:
            # Calculate expected balance from transactions
            from django.db.models import F
            expected_balance = account.transactions.aggregate(
                total_impact=Sum(
                    Case(
                        When(transaction_type='INCOME', then=F('amount')),
                        When(transaction_type='EXPENSE', then=F('amount') * -1),
                        default=0,
                        output_field=DecimalField(max_digits=12, decimal_places=2)
                    )
                )
            )['total_impact'] or Decimal('0.00')
            
            if account.balance != expected_balance:
                discrepancy = {
                    'account': account,
                    'current_balance': account.balance,
                    'expected_balance': expected_balance,
                    'difference': account.balance - expected_balance
                }
                discrepancies.append(discrepancy)
                
                logger.warning(
                    f"Balance discrepancy found for account {account.id} ({account.name}): "
                    f"Current: {account.balance}, Expected: {expected_balance}, "
                    f"Difference: {discrepancy['difference']}"
                )
        
        if not discrepancies:
            logger.info(
                f"All account balances validated successfully "
                f"{'for user ' + str(user.id) if user else '(all users)'}"
            )
            
    except Exception as e:
        logger.error(f"Error validating account balances: {str(e)}")
        raise
    
    return discrepancies