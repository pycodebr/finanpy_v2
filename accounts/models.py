from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

User = get_user_model()


class Account(models.Model):
    """
    Account model representing user financial accounts (bank accounts, credit cards, etc.).
    
    This model stores information about user's financial accounts including balances,
    account types, and currency settings. Each account is user-scoped for data isolation.
    
    Schema from PRD:
    - ForeignKey to User for data isolation
    - Name and account type classification
    - Balance tracking with decimal precision
    - Currency support for international users
    - Active/inactive status for account lifecycle management
    - Timestamps for audit trail
    """
    
    # Account type choices based on common financial account types
    ACCOUNT_TYPE_CHOICES = [
        ('checking', 'Conta Corrente'),
        ('savings', 'Conta Poupança'),
        ('credit_card', 'Cartão de Crédito'),
        ('investment', 'Conta de Investimento'),
        ('cash', 'Dinheiro'),
    ]
    
    # Currency choices - can be extended as needed
    CURRENCY_CHOICES = [
        ('USD', 'Dólar Americano'),
        ('EUR', 'Euro'),
        ('BRL', 'Real Brasileiro'),
        ('GBP', 'Libra Esterlina'),
        ('CAD', 'Dólar Canadense'),
    ]
    
    # Core fields following PRD schema
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='accounts',
        help_text='Owner of this account'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome',
        help_text='Nome descritivo para a conta (ex.: "Conta Corrente Itaú", "Fundo de Emergência")'
    )
    
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        verbose_name='Tipo de Conta',
        help_text='Tipo de conta para categorização e relatórios'
    )
    
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Saldo',
        help_text='Saldo atual da conta'
    )
    
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='BRL',
        verbose_name='Moeda',
        help_text='Código da moeda da conta (ISO 4217)'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativa',
        help_text='Se esta conta está ativa e deve ser incluída nos cálculos'
    )
    
    # Timestamps for audit trail
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em',
        help_text='Quando esta conta foi criada'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizada em',
        help_text='Quando esta conta foi modificada pela última vez'
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
        # Ensure unique account names per user
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_account_name_per_user'
            )
        ]
        # Add indexes for common queries
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'account_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        """Return string representation showing account name and type."""
        return f"{self.name} ({self.get_account_type_display()})"
    
    def clean(self):
        """Perform model-level validation."""
        super().clean()
        
        # Validate account name is not empty after stripping whitespace
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Account name cannot be empty.'})
        
        # Clean the name by stripping whitespace
        self.name = self.name.strip()
        
        # For credit cards, balance can be negative (representing debt)
        # For other account types, warn but allow negative balances (overdraft scenarios)
        if self.account_type != 'credit_card' and self.balance < 0:
            # Note: We could add a warning here or handle overdraft logic
            pass
    
    def save(self, *args, **kwargs):
        """Override save to ensure clean() validation is called."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def balance_display(self):
        """Return formatted balance with currency symbol in Brazilian format."""
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'BRL': 'R$',
            'GBP': '£',
            'CAD': 'C$',
        }
        symbol = currency_symbols.get(self.currency, self.currency)
        
        # Format number in Brazilian style: 1.234,56
        formatted_balance = f"{float(self.balance):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        return f"{symbol} {formatted_balance}"
    
    @property
    def is_debt_account(self):
        """Return True if this is a debt-type account (credit card)."""
        return self.account_type == 'credit_card'
    
    def get_transactions_queryset(self):
        """Return queryset of transactions for this account."""
        # This will be used when Transaction model is implemented
        # return self.transactions.select_related('category').order_by('-transaction_date')
        pass
