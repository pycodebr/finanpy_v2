from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from transactions.models import Transaction
from .models import Budget
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Transaction)
def update_budget_cache_on_transaction_save(sender, instance, created, **kwargs):
    """
    Update budget cache when transactions are saved.
    
    This signal is triggered whenever a Transaction is created or updated.
    It finds all budgets that might be affected by this transaction and
    refreshes their cached spent amounts for accurate budget tracking.
    
    Args:
        sender: Transaction model class
        instance: Transaction instance that was saved
        created: Boolean indicating if this is a new transaction
        **kwargs: Additional signal arguments
    """
    try:
        # Only process expense transactions as they affect budget spending
        if instance.transaction_type != 'EXPENSE':
            return
        
        # Find budgets that might be affected by this transaction
        affected_budgets = Budget.objects.filter(
            user=instance.user,
            category=instance.category,
            is_active=True,
            start_date__lte=instance.transaction_date,
            end_date__gte=instance.transaction_date
        ).select_related('category')
        
        # Also check parent category budgets (if transaction category is a subcategory)
        if hasattr(instance.category, 'parent') and instance.category.parent:
            parent_budgets = Budget.objects.filter(
                user=instance.user,
                category=instance.category.parent,
                is_active=True,
                start_date__lte=instance.transaction_date,
                end_date__gte=instance.transaction_date
            )
            affected_budgets = affected_budgets.union(parent_budgets)
        
        # Refresh cache for all affected budgets
        for budget in affected_budgets:
            try:
                budget.refresh_spent_amount()
                logger.info(
                    f"Updated budget cache for '{budget.name}' "
                    f"after transaction {'creation' if created else 'update'}: "
                    f"{instance.description} - {instance.amount}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to update budget cache for '{budget.name}': {str(e)}"
                )
                
    except Exception as e:
        logger.error(
            f"Error in update_budget_cache_on_transaction_save signal: {str(e)}"
        )


@receiver(post_delete, sender=Transaction)
def update_budget_cache_on_transaction_delete(sender, instance, **kwargs):
    """
    Update budget cache when transactions are deleted.
    
    This signal is triggered whenever a Transaction is deleted.
    It finds all budgets that were affected by this transaction and
    refreshes their cached spent amounts.
    
    Args:
        sender: Transaction model class
        instance: Transaction instance that was deleted
        **kwargs: Additional signal arguments
    """
    try:
        # Only process expense transactions
        if instance.transaction_type != 'EXPENSE':
            return
        
        # Find budgets that were affected by this transaction
        affected_budgets = Budget.objects.filter(
            user=instance.user,
            category=instance.category,
            is_active=True,
            start_date__lte=instance.transaction_date,
            end_date__gte=instance.transaction_date
        ).select_related('category')
        
        # Also check parent category budgets
        if hasattr(instance.category, 'parent') and instance.category.parent:
            parent_budgets = Budget.objects.filter(
                user=instance.user,
                category=instance.category.parent,
                is_active=True,
                start_date__lte=instance.transaction_date,
                end_date__gte=instance.transaction_date
            )
            affected_budgets = affected_budgets.union(parent_budgets)
        
        # Refresh cache for all affected budgets
        for budget in affected_budgets:
            try:
                budget.refresh_spent_amount()
                logger.info(
                    f"Updated budget cache for '{budget.name}' "
                    f"after transaction deletion: {instance.description} - {instance.amount}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to update budget cache for '{budget.name}': {str(e)}"
                )
                
    except Exception as e:
        logger.error(
            f"Error in update_budget_cache_on_transaction_delete signal: {str(e)}"
        )


@receiver(post_save, sender=Budget)
def clear_budget_cache_on_budget_save(sender, instance, created, **kwargs):
    """
    Clear budget cache when budget is saved to ensure fresh calculations.
    
    This signal ensures that when a budget is created or its parameters
    are changed (like dates or planned amount), the cache is cleared so
    that the next access will recalculate the spent amount.
    
    Args:
        sender: Budget model class
        instance: Budget instance that was saved
        created: Boolean indicating if this is a new budget
        **kwargs: Additional signal arguments
    """
    try:
        # Clear cache for fresh calculations, but only if it's an update
        # (not creation, as new budgets don't have cache yet)
        if not created and instance.pk:
            instance.clear_cache()
            logger.debug(
                f"Cleared cache for budget '{instance.name}' after update"
            )
    except Exception as e:
        logger.error(
            f"Error in clear_budget_cache_on_budget_save signal: {str(e)}"
        )


def refresh_all_budget_caches(user=None):
    """
    Utility function to refresh cache for all budgets.
    
    This function can be called manually when needed, for example
    after bulk operations or data migrations.
    
    Args:
        user: Optional user to limit cache refresh to specific user's budgets
    """
    try:
        budgets = Budget.objects.filter(is_active=True)
        
        if user:
            budgets = budgets.filter(user=user)
        
        budgets = budgets.select_related('category')
        
        refreshed_count = 0
        for budget in budgets:
            try:
                budget.refresh_spent_amount()
                refreshed_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to refresh cache for budget '{budget.name}': {str(e)}"
                )
        
        logger.info(
            f"Successfully refreshed cache for {refreshed_count} budgets"
            + (f" for user {user.username}" if user else "")
        )
        
        return refreshed_count
        
    except Exception as e:
        logger.error(f"Error in refresh_all_budget_caches: {str(e)}")
        return 0


def clear_all_budget_caches(user=None):
    """
    Utility function to clear cache for all budgets.
    
    This function forces all budgets to recalculate their spent amounts
    on next access, useful for debugging or after system changes.
    
    Args:
        user: Optional user to limit cache clearing to specific user's budgets
    """
    try:
        budgets = Budget.objects.filter(is_active=True)
        
        if user:
            budgets = budgets.filter(user=user)
        
        cleared_count = 0
        for budget in budgets:
            try:
                budget.clear_cache()
                cleared_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to clear cache for budget '{budget.name}': {str(e)}"
                )
        
        logger.info(
            f"Successfully cleared cache for {cleared_count} budgets"
            + (f" for user {user.username}" if user else "")
        )
        
        return cleared_count
        
    except Exception as e:
        logger.error(f"Error in clear_all_budget_caches: {str(e)}")
        return 0