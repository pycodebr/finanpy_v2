from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from .models import Account


class AccountForm(forms.ModelForm):
    """
    Form for creating and updating Account instances.
    
    Provides custom validation for account data including balance validation,
    name uniqueness per user, and proper decimal handling for financial amounts.
    """
    
    class Meta:
        model = Account
        fields = ['name', 'account_type', 'balance', 'currency']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Digite o nome da conta (ex.: "Conta Corrente Itaú", "Fundo de Emergência")',
                'maxlength': 100,
            }),
            'account_type': forms.Select(attrs={
                'class': 'form-input',
            }),
            'balance': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '-999999999.99',
                'max': '999999999.99',
            }),
            'currency': forms.Select(attrs={
                'class': 'form-input',
            }),
        }
        help_texts = {
            'name': 'Escolha um nome descritivo para identificar facilmente esta conta',
            'account_type': 'Selecione o tipo que melhor descreve esta conta',
            'balance': 'Digite o saldo atual (valores negativos são permitidos para contas de débito)',
            'currency': 'Escolha a moeda para esta conta',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set initial focus on name field
        self.fields['name'].widget.attrs['autofocus'] = True
        
        # Add required asterisks for required fields
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['class'] += ' required'
    
    def clean_name(self):
        """Validate account name."""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise ValidationError('Account name is required.')
        
        if len(name) < 2:
            raise ValidationError('Account name must be at least 2 characters long.')
        
        # Check for uniqueness within user's accounts
        if self.user:
            existing_accounts = Account.objects.filter(
                user=self.user,
                name__iexact=name,
                is_active=True
            )
            
            # If we're editing an existing account, exclude it from the check
            if self.instance and self.instance.pk:
                existing_accounts = existing_accounts.exclude(pk=self.instance.pk)
            
            if existing_accounts.exists():
                raise ValidationError(
                    'Você já possui uma conta ativa com este nome. '
                    'Escolha um nome diferente.'
                )
        
        return name
    
    def clean_balance(self):
        """Validate balance amount."""
        balance = self.cleaned_data.get('balance')
        
        if balance is None:
            return Decimal('0.00')
        
        try:
            # Convert to Decimal for precise financial calculations
            balance = Decimal(str(balance))
        except (InvalidOperation, TypeError):
            raise ValidationError('Por favor, digite um valor válido.')
        
        # Check for reasonable limits
        if balance < Decimal('-999999999.99'):
            raise ValidationError('Saldo não pode ser menor que -R$ 999.999.999,99')
        
        if balance > Decimal('999999999.99'):
            raise ValidationError('Saldo não pode ser maior que R$ 999.999.999,99')
        
        return balance
    
    def clean(self):
        """Perform cross-field validation."""
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')
        balance = cleaned_data.get('balance')
        
        # Validate balance based on account type
        if account_type and balance is not None:
            if account_type == 'credit_card':
                # For credit cards, negative balance represents available credit
                # Positive balance represents debt owed
                if balance > Decimal('50000.00'):
                    raise ValidationError({
                        'balance': 'O saldo do cartão de crédito parece muito alto. '
                                 'Verifique o valor.'
                    })
            else:
                # For other account types, warn about large negative balances
                if balance < Decimal('-10000.00'):
                    # This is a warning, not an error - allow it but flag it
                    pass
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save the account instance."""
        instance = super().save(commit=False)
        
        if self.user:
            instance.user = self.user
        
        if commit:
            instance.save()
        
        return instance


class AccountFilterForm(forms.Form):
    """
    Form for filtering accounts in the list view.
    
    Allows users to filter their accounts by type, currency, and active status.
    """
    
    account_type = forms.ChoiceField(
        choices=[('', 'Todos os Tipos')] + Account.ACCOUNT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input form-select',
            'onchange': 'this.form.submit();'
        })
    )
    
    currency = forms.ChoiceField(
        choices=[('', 'Todas as Moedas')] + Account.CURRENCY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input form-select',
            'onchange': 'this.form.submit();'
        })
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'Todas as Contas'),
            ('active', 'Apenas Ativas'),
            ('inactive', 'Apenas Inativas'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input form-select',
            'onchange': 'this.form.submit();'
        })
    )