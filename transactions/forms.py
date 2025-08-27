from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from datetime import date
from .models import Transaction
from accounts.models import Account
from categories.models import Category

User = get_user_model()


class TransactionForm(forms.ModelForm):
    """
    Form for creating and editing transactions with proper validation.
    
    Features:
    - Dynamic category filtering by transaction type
    - Client-side currency formatting
    - User-scoped account and category choices
    - Comprehensive validation
    - Clean error handling
    """
    
    class Meta:
        model = Transaction
        fields = [
            'transaction_type', 'account', 'category', 'amount', 
            'description', 'transaction_date', 'notes'
        ]
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_transaction_type',
                'onchange': 'filterCategoriesByType()'
            }),
            'account': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0,00',
                'onblur': 'formatCurrency(this)',
                'onfocus': 'unformatCurrency(this)'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-input',
                'maxlength': '200',
                'placeholder': 'Descrição da transação'
            }),
            'transaction_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'max': date.today().isoformat()
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Observações adicionais (opcional)'
            }),
        }
    
    def __init__(self, user, *args, **kwargs):
        """Initialize form with user-scoped choices."""
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Filter account choices to user's active accounts
        self.fields['account'].queryset = Account.objects.filter(
            user=user, is_active=True
        ).order_by('name')
        
        # Filter category choices to user's active categories
        self.fields['category'].queryset = Category.objects.filter(
            user=user, is_active=True
        ).order_by('category_type', 'name')
        
        # Set empty labels
        self.fields['account'].empty_label = 'Selecione uma conta'
        self.fields['category'].empty_label = 'Selecione uma categoria'
        
        # If editing an existing transaction, filter categories by type
        if self.instance and self.instance.pk:
            self._filter_categories_by_type()
    
    def _filter_categories_by_type(self):
        """Filter categories based on transaction type."""
        if hasattr(self.instance, 'transaction_type') and self.instance.transaction_type:
            self.fields['category'].queryset = self.fields['category'].queryset.filter(
                category_type=self.instance.transaction_type
            )
    
    def clean_amount(self):
        """Clean and validate amount field."""
        amount = self.cleaned_data.get('amount')
        
        if not amount:
            raise ValidationError('Amount is required.')
        
        # Convert string to Decimal if needed (handles currency formatting)
        if isinstance(amount, str):
            # Remove currency symbols and formatting
            cleaned_amount = amount.replace('R$', '').replace(' ', '')
            cleaned_amount = cleaned_amount.replace('.', '').replace(',', '.')
            
            try:
                amount = Decimal(cleaned_amount)
            except (ValueError, InvalidOperation):
                raise ValidationError('Enter a valid amount.')
        
        if amount <= 0:
            raise ValidationError('Amount must be positive.')
        
        # Limit to 2 decimal places
        if amount.as_tuple().exponent < -2:
            raise ValidationError('Amount cannot have more than 2 decimal places.')
        
        return amount
    
    def clean_description(self):
        """Clean and validate description field."""
        description = self.cleaned_data.get('description', '').strip()
        
        if not description:
            raise ValidationError('Description is required.')
        
        if len(description) < 3:
            raise ValidationError('Description must be at least 3 characters long.')
        
        return description
    
    def clean_transaction_date(self):
        """Clean and validate transaction date."""
        transaction_date = self.cleaned_data.get('transaction_date')
        
        if not transaction_date:
            raise ValidationError('Transaction date is required.')
        
        if transaction_date > date.today():
            raise ValidationError('Transaction date cannot be in the future.')
        
        return transaction_date
    
    def clean(self):
        """Perform cross-field validation and assign user to instance early."""
        cleaned_data = super().clean()
        
        # Assign user to instance early to avoid RelatedObjectDoesNotExist errors
        # during model validation
        if not hasattr(self.instance, 'user') or not self.instance.user:
            self.instance.user = self.user
        
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')
        account = cleaned_data.get('account')
        
        # Validate category matches transaction type
        if transaction_type and category:
            if category.category_type != transaction_type:
                raise ValidationError({
                    'category': f'Selected category is not compatible with {transaction_type.lower()} transactions.'
                })
        
        # Validate user ownership of account and category
        if account and account.user != self.user:
            raise ValidationError({
                'account': 'Selected account does not belong to you.'
            })
        
        if category and category.user != self.user:
            raise ValidationError({
                'category': 'Selected category does not belong to you.'
            })
        
        # Validate account is active
        if account and not account.is_active:
            raise ValidationError({
                'account': 'Selected account is inactive and cannot be used.'
            })
        
        # Validate category is active
        if category and not category.is_active:
            raise ValidationError({
                'category': 'Selected category is inactive and cannot be used.'
            })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save transaction with user assignment."""
        transaction = super().save(commit=False)
        
        # Ensure user is set - this is critical for the relationship
        if not self.user:
            raise ValidationError("User is required to create transaction")
        
        # Set user if not already set
        if not hasattr(transaction, 'user') or not transaction.user:
            transaction.user = self.user
        
        # Explicitly set user_id as well for safety
        if not transaction.user_id:
            transaction.user_id = self.user.id
        
        if commit:
            transaction.save()
        
        return transaction


class TransactionFilterForm(forms.Form):
    """
    Form for filtering transactions with date ranges, categories, accounts, and types.
    
    Features:
    - Date range filtering
    - Account and category filtering
    - Transaction type filtering
    - User-scoped choices
    - Clean parameter handling
    """
    
    date_from = forms.DateField(
        required=False,
        label='Data inicial',
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'placeholder': 'Data inicial'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        label='Data final',
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'placeholder': 'Data final'
        })
    )
    
    account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        label='Conta',
        empty_label='Todas as contas',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label='Categoria',
        empty_label='Todas as categorias',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    transaction_type = forms.ChoiceField(
        choices=[('', 'Todos os tipos')] + Transaction.TRANSACTION_TYPE_CHOICES,
        required=False,
        label='Tipo',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    search = forms.CharField(
        required=False,
        label='Buscar',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Buscar na descrição...'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        """Initialize form with user-scoped choices."""
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Filter choices to user's active accounts and categories
        self.fields['account'].queryset = Account.objects.filter(
            user=user, is_active=True
        ).order_by('name')
        
        self.fields['category'].queryset = Category.objects.filter(
            user=user, is_active=True
        ).order_by('category_type', 'name')
    
    def clean(self):
        """Validate date range."""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError('Start date must be before or equal to end date.')
        
        return cleaned_data
    
    def get_filters(self):
        """
        Return dictionary of filters for QuerySet filtering.
        
        Returns:
            Dict with non-empty filter parameters
        """
        if not self.is_valid():
            return {}
        
        filters = {}
        
        # Date range filters
        if self.cleaned_data.get('date_from'):
            filters['transaction_date__gte'] = self.cleaned_data['date_from']
        
        if self.cleaned_data.get('date_to'):
            filters['transaction_date__lte'] = self.cleaned_data['date_to']
        
        # Account filter
        if self.cleaned_data.get('account'):
            filters['account'] = self.cleaned_data['account']
        
        # Category filter
        if self.cleaned_data.get('category'):
            filters['category'] = self.cleaned_data['category']
        
        # Transaction type filter
        if self.cleaned_data.get('transaction_type'):
            filters['transaction_type'] = self.cleaned_data['transaction_type']
        
        return filters
    
    def get_search_term(self):
        """Return search term for description filtering."""
        return self.cleaned_data.get('search', '').strip() if self.is_valid() else ''