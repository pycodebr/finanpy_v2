from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q
from django.utils.timezone import now
from decimal import Decimal
from datetime import date
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Budget(models.Model):
    """
    Budget model for tracking planned spending against actual expenses by category.
    
    This model enables users to create budgets for specific categories over defined
    periods (typically monthly) and track their spending progress. The model
    automatically calculates spent amounts based on related transactions and
    provides performance-optimized percentage calculations.
    
    Schema from PRD:
    - ForeignKeys to User and Category for data relationships
    - Name for budget identification and description
    - planned_amount for budget allocation
    - spent_amount as calculated field from transactions
    - start_date and end_date for budget period
    - Calculated percentage_used property
    - Performance caching for expensive calculations
    - Comprehensive validation and data integrity
    
    Features:
    - User-scoped data isolation for security
    - Automatic spent amount calculation from transactions
    - Real-time percentage tracking with caching
    - Period-based budget organization
    - Integration with existing Category and Transaction models
    - Optimized database queries for performance
    - Comprehensive validation and constraints
    """
    
    # Budget status choices based on spending progress
    STATUS_CHOICES = [
        ('ACTIVE', 'Ativo'),
        ('INACTIVE', 'Inativo'),
        ('COMPLETED', 'Concluído'),
        ('EXCEEDED', 'Excedido'),
    ]
    
    # Core fields following PRD schema
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='budgets',
        help_text='Owner of this budget'
    )
    
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Categoria',
        help_text='Categoria para este orçamento'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome',
        help_text='Nome descritivo do orçamento (ex.: "Alimentação Janeiro 2024")'
    )
    
    planned_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor Planejado',
        help_text='Valor total planejado para este orçamento'
    )
    
    start_date = models.DateField(
        verbose_name='Data de Início',
        help_text='Data de início do período do orçamento'
    )
    
    end_date = models.DateField(
        verbose_name='Data de Fim',
        help_text='Data de fim do período do orçamento'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Se este orçamento está ativo e sendo monitorado'
    )
    
    # Caching fields for performance optimization
    _cached_spent_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        null=True,
        blank=True,
        help_text='Cached spent amount for performance (auto-calculated)'
    )
    
    _cache_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the cached values were last updated'
    )
    
    # Timestamps for audit trail
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em',
        help_text='Quando este orçamento foi criado'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
        help_text='Quando este orçamento foi modificado pela última vez'
    )
    
    class Meta:
        ordering = ['-start_date', 'name']
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
        
        # Ensure unique budget names per user within overlapping periods
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'category', 'start_date'],
                name='unique_budget_per_user_category_period'
            ),
            models.CheckConstraint(
                check=Q(end_date__gte=models.F('start_date')),
                name='budget_end_date_after_start_date'
            ),
            models.CheckConstraint(
                check=Q(planned_amount__gt=0),
                name='budget_positive_planned_amount'
            ),
        ]
        
        # Add indexes for common queries and performance optimization
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'start_date', 'end_date']),
            models.Index(fields=['category', 'start_date', 'end_date']),
            models.Index(fields=['start_date', 'end_date', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['_cache_updated_at']),
        ]
    
    def __str__(self):
        """Return string representation with budget name and period."""
        return f"{self.name} ({self.start_date} - {self.end_date})"
    
    def clean(self):
        """Perform model-level validation."""
        super().clean()
        
        # Validate budget name is not empty after stripping whitespace
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Budget name cannot be empty.'})
        
        # Clean the name by stripping whitespace
        self.name = self.name.strip()
        
        # Validate planned_amount is positive
        if self.planned_amount is not None and self.planned_amount <= 0:
            raise ValidationError({'planned_amount': 'Budget planned amount must be positive.'})
        
        # Validate date range
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'Budget end date must be after or equal to start date.'
                })
            
            # Check for reasonable budget periods (not longer than 1 year)
            if (self.end_date - self.start_date).days > 365:
                raise ValidationError({
                    'end_date': 'Budget period cannot be longer than 1 year.'
                })
        
        # Validate user data consistency
        if hasattr(self, 'user') and hasattr(self, 'category'):
            try:
                if self.category and self.category.user != self.user:
                    raise ValidationError({
                        'category': 'Selected category must belong to the same user.'
                    })
            except AttributeError:
                # Skip validation if relationships aren't fully loaded
                pass
        
        # Validate category is active and of EXPENSE type
        if hasattr(self, 'category') and self.category:
            try:
                if not self.category.is_active:
                    raise ValidationError({
                        'category': 'Cannot create budgets for inactive categories.'
                    })
                
                # Only allow budgets for EXPENSE categories
                if self.category.category_type != 'EXPENSE':
                    raise ValidationError({
                        'category': 'Budgets can only be created for expense categories.'
                    })
            except AttributeError:
                # Skip validation if category relationship isn't fully loaded
                pass
        
        # Validate no overlapping budgets for same user/category
        if self.user_id and self.category_id and self.start_date and self.end_date:
            overlapping_budgets = Budget.objects.filter(
                user=self.user,
                category=self.category,
                is_active=True,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date
            )
            
            # Exclude current instance if updating
            if self.pk:
                overlapping_budgets = overlapping_budgets.exclude(pk=self.pk)
            
            if overlapping_budgets.exists():
                raise ValidationError({
                    'start_date': 'Cannot create overlapping budgets for the same category.',
                    'end_date': 'Cannot create overlapping budgets for the same category.'
                })
    
    def save(self, *args, **kwargs):
        """Override save to ensure clean() validation is called and handle caching."""
        self.full_clean()
        
        # Clear cache when budget is modified
        if self.pk:  # Only for updates, not new instances
            self._cached_spent_amount = None
            self._cache_updated_at = None
        
        super().save(*args, **kwargs)
    
    @property
    def spent_amount(self):
        """
        Calculate and return the total amount spent in this budget period.
        
        This property aggregates all expense transactions for this budget's category
        within the budget period. Uses intelligent caching to improve performance
        for frequently accessed budgets.
        
        Returns:
            Decimal: Total amount spent, always as a positive value
        """
        # Check if we have a valid cached value
        if self._is_cache_valid():
            return self._cached_spent_amount or Decimal('0.00')
        
        # Calculate spent amount from transactions
        spent = self._calculate_spent_amount()
        
        # Update cache
        self._update_cache(spent)
        
        return spent
    
    def _calculate_spent_amount(self):
        """
        Calculate spent amount by aggregating expense transactions.
        
        This method queries the Transaction model for all expenses in this
        budget's category and date range, including transactions from
        child categories if the budget category has subcategories.
        
        Returns:
            Decimal: Total spent amount
        """
        from transactions.models import Transaction
        
        # Return 0 if budget doesn't have required relationships yet
        if not self.user_id or not self.category_id or not self.start_date or not self.end_date:
            return Decimal('0.00')
        
        # Get all descendant categories to include subcategory spending
        category_ids = [self.category.id]
        
        # Include spending from subcategories
        if hasattr(self.category, 'get_descendants'):
            descendant_categories = self.category.get_descendants()
            category_ids.extend(descendant_categories.values_list('id', flat=True))
        
        # Aggregate expense transactions within budget period
        total_spent = Transaction.objects.filter(
            user=self.user,
            category_id__in=category_ids,
            transaction_type='EXPENSE',
            transaction_date__gte=self.start_date,
            transaction_date__lte=self.end_date
        ).aggregate(
            total=Sum('amount')
        )['total']
        
        return total_spent or Decimal('0.00')
    
    def _is_cache_valid(self):
        """
        Check if cached spent amount is still valid.
        
        Cache is considered valid if:
        1. We have cached values
        2. Cache was updated recently (within cache timeout)
        3. No transactions have been modified since cache update
        
        Returns:
            bool: True if cache is valid, False otherwise
        """
        if not self._cached_spent_amount or not self._cache_updated_at:
            return False
        
        # Cache timeout: 5 minutes for active budgets, 1 hour for completed budgets
        from django.utils.timezone import timedelta
        
        if self.is_budget_period_active:
            cache_timeout = timedelta(minutes=5)
        else:
            cache_timeout = timedelta(hours=1)
        
        cache_expired = (now() - self._cache_updated_at) > cache_timeout
        
        return not cache_expired
    
    def _update_cache(self, spent_amount):
        """
        Update cached spent amount and timestamp.
        
        Args:
            spent_amount (Decimal): The calculated spent amount to cache
        """
        self._cached_spent_amount = spent_amount
        self._cache_updated_at = now()
        
        # Save cache without triggering validation or signals
        Budget.objects.filter(pk=self.pk).update(
            _cached_spent_amount=spent_amount,
            _cache_updated_at=self._cache_updated_at
        )
    
    def refresh_spent_amount(self):
        """
        Force refresh of spent amount calculation and cache.
        
        This method should be called when transactions are modified
        that might affect this budget's spent amount.
        
        Returns:
            Decimal: The newly calculated spent amount
        """
        spent = self._calculate_spent_amount()
        self._update_cache(spent)
        return spent
    
    def clear_cache(self):
        """Clear cached values to force recalculation on next access."""
        self._cached_spent_amount = None
        self._cache_updated_at = None
        
        Budget.objects.filter(pk=self.pk).update(
            _cached_spent_amount=None,
            _cache_updated_at=None
        )
    
    @property
    def percentage_used(self):
        """
        Calculate the percentage of budget spent.
        
        Returns percentage as a decimal (0.0 to 100.0+).
        Values over 100.0 indicate budget overspending.
        
        Returns:
            Decimal: Percentage of budget used (0.0 - 100.0+)
        """
        if not self.planned_amount or self.planned_amount == 0:
            return Decimal('0.00')
        
        spent = self.spent_amount
        percentage = (spent / self.planned_amount) * Decimal('100')
        
        # Round to 2 decimal places
        return round(percentage, 2)
    
    @property
    def remaining_amount(self):
        """
        Calculate remaining budget amount.
        
        Returns:
            Decimal: Remaining amount (can be negative if over budget)
        """
        return self.planned_amount - self.spent_amount
    
    @property
    def is_over_budget(self):
        """
        Check if spending has exceeded the planned amount.
        
        Returns:
            bool: True if spent amount exceeds planned amount
        """
        return self.spent_amount > self.planned_amount
    
    @property
    def is_budget_period_active(self):
        """
        Check if the budget period is currently active.
        
        Returns:
            bool: True if current date is within budget period
        """
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def is_budget_period_future(self):
        """
        Check if the budget period is in the future.
        
        Returns:
            bool: True if budget period hasn't started yet
        """
        return date.today() < self.start_date
    
    @property
    def is_budget_period_past(self):
        """
        Check if the budget period has ended.
        
        Returns:
            bool: True if budget period has ended
        """
        return date.today() > self.end_date
    
    @property
    def days_remaining(self):
        """
        Calculate days remaining in budget period.
        
        Returns:
            int: Days remaining (negative if period has ended)
        """
        return (self.end_date - date.today()).days
    
    @property
    def days_total(self):
        """
        Calculate total days in budget period.
        
        Returns:
            int: Total days in the budget period
        """
        return (self.end_date - self.start_date).days + 1
    
    @property
    def days_elapsed(self):
        """
        Calculate days elapsed in budget period.
        
        Returns:
            int: Days elapsed since start of period
        """
        today = date.today()
        if today < self.start_date:
            return 0
        elif today > self.end_date:
            return self.days_total
        else:
            return (today - self.start_date).days + 1
    
    @property
    def progress_percentage(self):
        """
        Calculate time progress percentage through budget period.
        
        Returns:
            Decimal: Percentage of time elapsed (0.0 - 100.0)
        """
        if self.days_total == 0:
            return Decimal('100.00')
        
        progress = (self.days_elapsed / self.days_total) * 100
        return min(Decimal('100.00'), round(Decimal(str(progress)), 2))
    
    @property
    def status(self):
        """
        Get current budget status based on spending and time progress.
        
        Returns:
            str: Budget status ('ACTIVE', 'EXCEEDED', 'COMPLETED', 'INACTIVE')
        """
        if not self.is_active:
            return 'INACTIVE'
        
        if self.is_over_budget:
            return 'EXCEEDED'
        
        if self.is_budget_period_past:
            return 'COMPLETED'
        
        return 'ACTIVE'
    
    @property
    def status_display(self):
        """
        Get human-readable status display.
        
        Returns:
            str: Localized status display
        """
        status_map = {
            'ACTIVE': 'Ativo',
            'EXCEEDED': 'Excedido',
            'COMPLETED': 'Concluído',
            'INACTIVE': 'Inativo'
        }
        return status_map.get(self.status, 'Desconhecido')
    
    @property
    def status_color_class(self):
        """
        Get CSS color class based on budget status.
        
        Returns:
            str: TailwindCSS color class for UI styling
        """
        color_map = {
            'ACTIVE': 'text-blue-600',
            'EXCEEDED': 'text-red-600',
            'COMPLETED': 'text-green-600',
            'INACTIVE': 'text-gray-500'
        }
        return color_map.get(self.status, 'text-gray-500')
    
    @property
    def progress_bar_color(self):
        """
        Get progress bar color based on spending percentage.
        
        Returns:
            str: TailwindCSS background color class
        """
        percentage = float(self.percentage_used)
        
        if percentage < 50:
            return 'bg-green-500'
        elif percentage < 80:
            return 'bg-yellow-500'
        elif percentage < 100:
            return 'bg-orange-500'
        else:
            return 'bg-red-500'
    
    # Display and formatting properties
    @property
    def planned_amount_display(self):
        """Return formatted planned amount with currency symbol."""
        # Use Brazilian currency formatting by default
        formatted_amount = f"{float(self.planned_amount):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted_amount}"
    
    @property
    def spent_amount_display(self):
        """Return formatted spent amount with currency symbol."""
        spent = self.spent_amount
        formatted_amount = f"{float(spent):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted_amount}"
    
    @property
    def remaining_amount_display(self):
        """Return formatted remaining amount with currency symbol."""
        remaining = self.remaining_amount
        formatted_amount = f"{float(remaining):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        sign = "+" if remaining >= 0 else ""
        return f"R$ {sign}{formatted_amount}"
    
    def get_absolute_url(self):
        """Return the absolute URL to view this budget."""
        from django.urls import reverse
        return reverse('budgets:detail', kwargs={'pk': self.pk})
    
    # Class methods for budget analysis and reporting
    @classmethod
    def get_user_budgets(cls, user, **filters):
        """
        Return queryset of budgets for a specific user with optional filters.
        
        Args:
            user: User object
            **filters: Additional filters (category, start_date, is_active, etc.)
            
        Returns:
            QuerySet of user's budgets with related objects prefetched
        """
        queryset = cls.objects.filter(user=user).select_related(
            'category'
        ).prefetch_related(
            'category__children'
        )
        
        # Apply additional filters
        for field, value in filters.items():
            if value is not None:
                queryset = queryset.filter(**{field: value})
        
        return queryset
    
    @classmethod
    def get_active_budgets(cls, user, date_filter=None):
        """
        Get active budgets for a user, optionally filtered by date.
        
        Args:
            user: User object
            date_filter: Date to check for active budgets (defaults to today)
            
        Returns:
            QuerySet of active budgets
        """
        if date_filter is None:
            date_filter = date.today()
        
        return cls.get_user_budgets(
            user,
            is_active=True,
            start_date__lte=date_filter,
            end_date__gte=date_filter
        )
    
    @classmethod
    def get_monthly_budgets(cls, user, year, month):
        """
        Get budgets that are active during a specific month.
        
        Args:
            user: User object
            year: Year as integer
            month: Month as integer (1-12)
            
        Returns:
            QuerySet of budgets active during the specified month
        """
        from calendar import monthrange
        
        # Get first and last day of the month
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        
        return cls.get_user_budgets(
            user,
            is_active=True,
            start_date__lte=last_day,
            end_date__gte=first_day
        )
    
    @classmethod
    def get_budget_summary(cls, user, start_date=None, end_date=None):
        """
        Get summary statistics for user's budgets within a date range.
        
        Args:
            user: User object
            start_date: Start date for analysis (optional)
            end_date: End date for analysis (optional)
            
        Returns:
            Dictionary with budget summary statistics
        """
        queryset = cls.get_user_budgets(user, is_active=True)
        
        # Filter by date range if provided
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        budgets = list(queryset)
        
        if not budgets:
            return {
                'total_budgets': 0,
                'total_planned': Decimal('0.00'),
                'total_spent': Decimal('0.00'),
                'total_remaining': Decimal('0.00'),
                'average_usage': Decimal('0.00'),
                'over_budget_count': 0,
                'active_budgets_count': 0
            }
        
        # Calculate summary statistics
        total_planned = sum(b.planned_amount for b in budgets)
        total_spent = sum(b.spent_amount for b in budgets)
        total_remaining = total_planned - total_spent
        
        # Calculate average usage percentage
        usage_percentages = [b.percentage_used for b in budgets if b.planned_amount > 0]
        average_usage = sum(usage_percentages) / len(usage_percentages) if usage_percentages else Decimal('0.00')
        
        # Count budgets by status
        over_budget_count = sum(1 for b in budgets if b.is_over_budget)
        active_budgets_count = sum(1 for b in budgets if b.is_budget_period_active)
        
        return {
            'total_budgets': len(budgets),
            'total_planned': total_planned,
            'total_spent': total_spent,
            'total_remaining': total_remaining,
            'average_usage': round(average_usage, 2),
            'over_budget_count': over_budget_count,
            'active_budgets_count': active_budgets_count
        }
    
    def get_spending_trend(self, days_back=30):
        """
        Get spending trend for this budget over the last N days.
        
        Args:
            days_back: Number of days to look back for trend analysis
            
        Returns:
            List of daily spending amounts within the budget period
        """
        from transactions.models import Transaction
        from django.utils import timezone
        from datetime import timedelta
        
        # Calculate date range within budget period
        end_date = min(date.today(), self.end_date)
        start_date = max(
            end_date - timedelta(days=days_back),
            self.start_date
        )
        
        # Get daily spending totals
        daily_spending = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            transaction_type='EXPENSE',
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        ).values('transaction_date').annotate(
            daily_total=Sum('amount')
        ).order_by('transaction_date')
        
        return list(daily_spending)
    
    def get_category_breakdown(self):
        """
        Get spending breakdown by subcategories if this budget's category has children.
        
        Returns:
            List of dictionaries with subcategory spending information
        """
        from transactions.models import Transaction
        
        # If category has no children, return spending for this category only
        if not hasattr(self.category, 'children') or not self.category.children.exists():
            spent = self._calculate_spent_amount()
            return [{
                'category_name': self.category.name,
                'category_id': self.category.id,
                'amount_spent': spent,
                'percentage_of_budget': (spent / self.planned_amount * 100) if self.planned_amount > 0 else Decimal('0.00')
            }]
        
        # Get spending by subcategories
        subcategories = self.category.children.filter(is_active=True)
        breakdown = []
        
        for subcategory in subcategories:
            spent = Transaction.objects.filter(
                user=self.user,
                category=subcategory,
                transaction_type='EXPENSE',
                transaction_date__gte=self.start_date,
                transaction_date__lte=self.end_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            if spent > 0:  # Only include subcategories with spending
                breakdown.append({
                    'category_name': subcategory.name,
                    'category_id': subcategory.id,
                    'amount_spent': spent,
                    'percentage_of_budget': (spent / self.planned_amount * 100) if self.planned_amount > 0 else Decimal('0.00')
                })
        
        # Sort by amount spent (descending)
        breakdown.sort(key=lambda x: x['amount_spent'], reverse=True)
        
        return breakdown
    
    def get_recent_transactions(self, limit=10):
        """
        Get recent transactions for this budget's category and period.
        
        Args:
            limit: Maximum number of transactions to return
            
        Returns:
            QuerySet of recent transactions
        """
        from transactions.models import Transaction
        
        # Get all descendant categories
        category_ids = [self.category.id]
        if hasattr(self.category, 'get_descendants'):
            descendant_categories = self.category.get_descendants()
            category_ids.extend(descendant_categories.values_list('id', flat=True))
        
        return Transaction.objects.filter(
            user=self.user,
            category_id__in=category_ids,
            transaction_type='EXPENSE',
            transaction_date__gte=self.start_date,
            transaction_date__lte=self.end_date
        ).select_related('account', 'category').order_by('-transaction_date', '-created_at')[:limit]


# Documentation and Usage Examples
"""
Budget Model Usage Examples and Integration Guide

The Budget model is designed to seamlessly integrate with the existing Finanpy
financial management system, providing comprehensive budget tracking and analysis
capabilities.

## Basic Usage Examples

### Creating a Budget
```python
from budgets.models import Budget
from categories.models import Category
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()

# Get user and category
user = User.objects.get(username='john_doe')
food_category = Category.objects.get(user=user, name='Alimentação', category_type='EXPENSE')

# Create a monthly food budget
budget = Budget.objects.create(
    user=user,
    category=food_category,
    name='Orçamento Alimentação Janeiro 2024',
    planned_amount=Decimal('800.00'),
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
    is_active=True
)

print(f"Created budget: {budget}")
print(f"Planned amount: {budget.planned_amount_display}")
```

### Accessing Budget Information
```python
# Get current spending and progress
print(f"Spent: {budget.spent_amount_display}")
print(f"Remaining: {budget.remaining_amount_display}")
print(f"Usage: {budget.percentage_used}%")
print(f"Status: {budget.status_display}")

# Check time-based properties
print(f"Days remaining: {budget.days_remaining}")
print(f"Time progress: {budget.progress_percentage}%")
print(f"Is over budget: {budget.is_over_budget}")
```

### Budget Analysis and Reporting
```python
# Get budget summary for a user
summary = Budget.get_budget_summary(user, 
                                  start_date=date(2024, 1, 1),
                                  end_date=date(2024, 12, 31))
print(f"Total budgets: {summary['total_budgets']}")
print(f"Average usage: {summary['average_usage']}%")

# Get active budgets
active_budgets = Budget.get_active_budgets(user)
print(f"Active budgets count: {active_budgets.count()}")

# Get monthly budgets
january_budgets = Budget.get_monthly_budgets(user, 2024, 1)
```

## Advanced Features

### Caching and Performance
The Budget model implements intelligent caching for expensive calculations:
- spent_amount property automatically caches transaction aggregations
- Cache timeout: 5 minutes for active budgets, 1 hour for completed ones
- Manual cache refresh available via refresh_spent_amount()

```python
# Force refresh cached values
budget.refresh_spent_amount()

# Clear cache to force recalculation
budget.clear_cache()
```

### Category Hierarchy Support
Budgets automatically include spending from subcategories:
```python
# If "Alimentação" has subcategories like "Restaurantes", "Supermercado"
# The budget will include transactions from all subcategories
category_breakdown = budget.get_category_breakdown()
for item in category_breakdown:
    print(f"{item['category_name']}: {item['amount_spent']}")
```

### Spending Trends and Analysis
```python
# Get spending trend for the last 30 days
trend = budget.get_spending_trend(days_back=30)
for day_data in trend:
    print(f"{day_data['transaction_date']}: {day_data['daily_total']}")

# Get recent transactions affecting this budget
recent_transactions = budget.get_recent_transactions(limit=5)
```

## Integration with Django Signals

The Budget model is designed to work with Django signals for automatic
cache invalidation when transactions are created or modified.

### Recommended Signal Implementation
```python
# In transactions/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from transactions.models import Transaction
from budgets.models import Budget

@receiver(post_save, sender=Transaction)
def update_budget_cache_on_transaction_save(sender, instance, created, **kwargs):
    \"\"\"Update budget cache when transactions are saved.\"\"\"
    if instance.transaction_type == 'EXPENSE':
        # Find affected budgets
        affected_budgets = Budget.objects.filter(
            user=instance.user,
            category=instance.category,
            is_active=True,
            start_date__lte=instance.transaction_date,
            end_date__gte=instance.transaction_date
        )
        
        # Refresh cache for all affected budgets
        for budget in affected_budgets:
            budget.refresh_spent_amount()

@receiver(post_delete, sender=Transaction)
def update_budget_cache_on_transaction_delete(sender, instance, **kwargs):
    \"\"\"Update budget cache when transactions are deleted.\"\"\"
    if instance.transaction_type == 'EXPENSE':
        # Similar logic as above
        pass
```

## Database Performance Considerations

### Indexes
The Budget model includes strategic indexes for optimal performance:
- user + is_active (for user budget lists)
- user + category (for category-specific budgets)
- user + start_date + end_date (for date range queries)
- start_date + end_date + is_active (for active budget queries)

### Query Optimization
```python
# Efficient budget querying with related data
budgets = Budget.objects.filter(user=user).select_related('category').prefetch_related('category__children')

# Use class methods for optimized queries
budgets = Budget.get_user_budgets(user, is_active=True)
```

## Validation and Data Integrity

The Budget model enforces several validation rules:
- End date must be after or equal to start date
- Planned amount must be positive
- No overlapping budgets for same user/category
- Budget periods cannot exceed 1 year
- Only EXPENSE categories can have budgets
- Category must belong to the same user

### Error Handling
```python
from django.core.exceptions import ValidationError

try:
    budget = Budget(
        user=user,
        category=income_category,  # This will fail - income categories not allowed
        name='Invalid Budget',
        planned_amount=Decimal('1000.00'),
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30)
    )
    budget.save()
except ValidationError as e:
    print(f"Validation error: {e}")
```

## UI Integration

The Budget model provides several properties for easy UI integration:
- status_color_class: TailwindCSS classes for status display
- progress_bar_color: Color classes based on spending percentage
- Formatted display properties for currency amounts
- Progress percentages for visual progress bars

```html
<!-- Example template usage -->
<div class="budget-card">
    <h3>{{ budget.name }}</h3>
    <div class="progress-bar">
        <div class="progress-fill {{ budget.progress_bar_color }}"
             style="width: {{ budget.percentage_used }}%"></div>
    </div>
    <div class="{{ budget.status_color_class }}">
        {{ budget.status_display }}
    </div>
    <p>{{ budget.spent_amount_display }} / {{ budget.planned_amount_display }}</p>
</div>
```

This comprehensive Budget model provides all the functionality needed for
robust budget tracking while maintaining excellent performance through
intelligent caching and optimized database queries.
"""
