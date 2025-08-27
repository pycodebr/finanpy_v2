from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum, Avg, Count, Q
from decimal import Decimal
from datetime import date, datetime, timedelta
from .models import Budget
from categories.models import Category
from transactions.models import Transaction

User = get_user_model()


class BudgetForm(forms.ModelForm):
    """
    Form for creating and updating budgets with comprehensive validation.
    
    This form provides:
    - Category selection limited to user's expense categories
    - Date validation with reasonable period constraints
    - Amount validation with minimum/maximum limits
    - Historical data preview for informed budget planning
    - Overlap prevention with existing budgets
    - User-scoped data filtering for security
    """
    
    class Meta:
        model = Budget
        fields = ['category', 'name', 'planned_amount', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex.: Orçamento Alimentação Janeiro 2024',
                'maxlength': 100
            }),
            'planned_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0.01',
                'max': '999999999.99',
                'placeholder': '0,00'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'category': forms.Select(attrs={
                'class': 'form-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }
    
    def __init__(self, user, *args, **kwargs):
        """
        Initialize form with user-scoped category choices and default values.
        
        Args:
            user: Current user for data scoping
            *args, **kwargs: Standard form arguments
        """
        self.user = user
        super().__init__(*args, **kwargs)
        
        # Limit category choices to user's active expense categories
        self.fields['category'].queryset = Category.objects.filter(
            user=user,
            category_type='EXPENSE',
            is_active=True
        ).order_by('name')
        
        # Set default date range to current month if creating new budget
        if not self.instance.pk:
            today = date.today()
            first_day = today.replace(day=1)
            
            # Calculate last day of current month
            if today.month == 12:
                last_day = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
            
            self.fields['start_date'].initial = first_day
            self.fields['end_date'].initial = last_day
        
        # Add help text with historical data preview
        self._add_historical_context()
    
    def _add_historical_context(self):
        """Add historical spending data as help text for informed budget planning."""
        if self.instance.pk and self.instance.category:
            # For existing budgets, show current spending
            current_spent = self.instance.spent_amount
            self.fields['planned_amount'].help_text = (
                f"Gasto atual: R$ {current_spent:,.2f}. "
                "Ajuste o valor planejado conforme necessário."
            )
        else:
            # For new budgets, provide general guidance
            self.fields['planned_amount'].help_text = (
                "Digite o valor que você planeja gastar nesta categoria no período selecionado. "
                "Considere seu histórico de gastos para definir um valor realista."
            )
        
        self.fields['start_date'].help_text = (
            "Data de início do período do orçamento. Geralmente o primeiro dia do mês."
        )
        self.fields['end_date'].help_text = (
            "Data de fim do período do orçamento. Não pode ser mais de 1 ano após o início."
        )
        self.fields['category'].help_text = (
            "Categoria de despesa para este orçamento. Apenas categorias ativas são mostradas."
        )
    
    def clean_name(self):
        """Validate and clean budget name."""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise ValidationError('O nome do orçamento é obrigatório.')
        
        if len(name) < 3:
            raise ValidationError('O nome deve ter pelo menos 3 caracteres.')
        
        return name
    
    def clean_planned_amount(self):
        """Validate planned amount with reasonable limits."""
        amount = self.cleaned_data.get('planned_amount')
        
        if not amount:
            raise ValidationError('O valor planejado é obrigatório.')
        
        if amount < Decimal('0.01'):
            raise ValidationError('O valor planejado deve ser maior que zero.')
        
        if amount > Decimal('999999999.99'):
            raise ValidationError('O valor planejado é muito alto.')
        
        return amount
    
    def clean_start_date(self):
        """Validate start date with reasonable constraints."""
        start_date = self.cleaned_data.get('start_date')
        
        if not start_date:
            raise ValidationError('A data de início é obrigatória.')
        
        # Allow budgets starting up to 1 year in the past or 2 years in the future
        min_date = date.today() - timedelta(days=365)
        max_date = date.today() + timedelta(days=730)
        
        if start_date < min_date:
            raise ValidationError(
                f'A data de início não pode ser anterior a {min_date.strftime("%d/%m/%Y")}.'
            )
        
        if start_date > max_date:
            raise ValidationError(
                f'A data de início não pode ser posterior a {max_date.strftime("%d/%m/%Y")}.'
            )
        
        return start_date
    
    def clean_end_date(self):
        """Validate end date in relation to start date."""
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')
        
        if not end_date:
            raise ValidationError('A data de fim é obrigatória.')
        
        if start_date and end_date < start_date:
            raise ValidationError('A data de fim deve ser igual ou posterior à data de início.')
        
        if start_date and (end_date - start_date).days > 365:
            raise ValidationError('O período do orçamento não pode ser maior que 1 ano.')
        
        return end_date
    
    def clean_category(self):
        """Validate category belongs to user and is expense type."""
        category = self.cleaned_data.get('category')
        
        if not category:
            raise ValidationError('A categoria é obrigatória.')
        
        if category.user != self.user:
            raise ValidationError('A categoria selecionada não pertence ao usuário atual.')
        
        if category.category_type != 'EXPENSE':
            raise ValidationError('Orçamentos só podem ser criados para categorias de despesa.')
        
        if not category.is_active:
            raise ValidationError('Não é possível criar orçamentos para categorias inativas.')
        
        return category
    
    def clean(self):
        """Perform cross-field validation and check for overlapping budgets."""
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Check for overlapping active budgets
        if category and start_date and end_date:
            overlapping_budgets = Budget.objects.filter(
                user=self.user,
                category=category,
                is_active=True,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            # Exclude current instance when updating
            if self.instance.pk:
                overlapping_budgets = overlapping_budgets.exclude(pk=self.instance.pk)
            
            if overlapping_budgets.exists():
                overlapping_budget = overlapping_budgets.first()
                raise ValidationError({
                    'category': f'Já existe um orçamento ativo para esta categoria no período de '
                               f'{overlapping_budget.start_date.strftime("%d/%m/%Y")} a '
                               f'{overlapping_budget.end_date.strftime("%d/%m/%Y")}.'
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save budget instance with user assignment."""
        budget = super().save(commit=False)
        budget.user = self.user
        
        if commit:
            budget.save()
        
        return budget
    
    def get_historical_data(self):
        """
        Get historical spending data for the selected category to help with budget planning.
        
        Returns:
            dict: Historical spending statistics
        """
        category = self.cleaned_data.get('category')
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        
        if not (category and start_date and end_date):
            return {}
        
        # Calculate number of days in budget period
        period_days = (end_date - start_date).days + 1
        
        # Get historical transactions for this category (last 12 months)
        historical_start = start_date - timedelta(days=365)
        
        transactions = Transaction.objects.filter(
            user=self.user,
            category=category,
            transaction_type='EXPENSE',
            transaction_date__gte=historical_start,
            transaction_date__lt=start_date
        )
        
        if not transactions.exists():
            return {
                'has_historical_data': False,
                'message': 'Nenhum histórico encontrado para esta categoria.'
            }
        
        # Calculate statistics
        stats = transactions.aggregate(
            total_spent=Sum('amount'),
            avg_transaction=Avg('amount'),
            transaction_count=Count('id')
        )
        
        total_days = (start_date - historical_start).days
        daily_avg = stats['total_spent'] / total_days if total_days > 0 else Decimal('0')
        
        # Estimate for budget period
        estimated_spending = daily_avg * period_days
        
        return {
            'has_historical_data': True,
            'period_days': period_days,
            'historical_total': stats['total_spent'],
            'historical_avg': stats['avg_transaction'],
            'transaction_count': stats['transaction_count'],
            'daily_average': daily_avg,
            'estimated_spending': estimated_spending,
            'recommended_budget': estimated_spending * Decimal('1.1')  # 10% buffer
        }


class BudgetFilterForm(forms.Form):
    """
    Form for filtering budget lists with various criteria.
    
    Provides filtering options for:
    - Status (active, completed, exceeded, etc.)
    - Category selection
    - Date range filtering
    - Search by name
    """
    
    STATUS_CHOICES = [
        ('', 'Todos os Status'),
        ('ACTIVE', 'Ativo'),
        ('EXCEEDED', 'Excedido'),
        ('COMPLETED', 'Concluído'),
        ('INACTIVE', 'Inativo'),
    ]
    
    PERIOD_CHOICES = [
        ('', 'Todos os Períodos'),
        ('current_month', 'Mês Atual'),
        ('last_month', 'Mês Passado'),
        ('current_year', 'Ano Atual'),
        ('last_year', 'Ano Passado'),
        ('custom', 'Período Personalizado'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Pesquisar por nome do orçamento...',
            'maxlength': 100
        }),
        label='Pesquisar'
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        }),
        label='Status'
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label='Todas as Categorias',
        widget=forms.Select(attrs={
            'class': 'form-input'
        }),
        label='Categoria'
    )
    
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        }),
        label='Período'
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        }),
        label='Data de Início'
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        }),
        label='Data de Fim'
    )
    
    def __init__(self, user, *args, **kwargs):
        """
        Initialize form with user-scoped category choices.
        
        Args:
            user: Current user for data scoping
        """
        self.user = user
        super().__init__(*args, **kwargs)
        
        # Set user-scoped category choices
        self.fields['category'].queryset = Category.objects.filter(
            user=user,
            category_type='EXPENSE',
            is_active=True
        ).order_by('name')
    
    def clean(self):
        """Validate custom date range when period is set to custom."""
        cleaned_data = super().clean()
        period = cleaned_data.get('period')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if period == 'custom':
            if not start_date:
                raise ValidationError({
                    'start_date': 'Data de início é obrigatória para período personalizado.'
                })
            if not end_date:
                raise ValidationError({
                    'end_date': 'Data de fim é obrigatória para período personalizado.'
                })
            if start_date and end_date and end_date < start_date:
                raise ValidationError({
                    'end_date': 'Data de fim deve ser igual ou posterior à data de início.'
                })
        
        return cleaned_data
    
    def get_date_range(self):
        """
        Get date range based on selected period.
        
        Returns:
            tuple: (start_date, end_date) or (None, None) if no period selected
        """
        period = self.cleaned_data.get('period')
        
        if period == 'custom':
            return self.cleaned_data.get('start_date'), self.cleaned_data.get('end_date')
        
        today = date.today()
        
        if period == 'current_month':
            start = today.replace(day=1)
            if today.month == 12:
                end = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(today.year, today.month + 1, 1) - timedelta(days=1)
            return start, end
        
        elif period == 'last_month':
            if today.month == 1:
                start = date(today.year - 1, 12, 1)
                end = date(today.year, 1, 1) - timedelta(days=1)
            else:
                start = date(today.year, today.month - 1, 1)
                end = today.replace(day=1) - timedelta(days=1)
            return start, end
        
        elif period == 'current_year':
            return date(today.year, 1, 1), date(today.year, 12, 31)
        
        elif period == 'last_year':
            return date(today.year - 1, 1, 1), date(today.year - 1, 12, 31)
        
        return None, None
    
    def apply_filters(self, queryset):
        """
        Apply filters to a budget queryset based on form data.
        
        Args:
            queryset: Base budget queryset to filter
            
        Returns:
            QuerySet: Filtered queryset
        """
        if not self.is_valid():
            return queryset
        
        # Search filter
        search = self.cleaned_data.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(category__name__icontains=search)
            )
        
        # Category filter
        category = self.cleaned_data.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Status filter
        status = self.cleaned_data.get('status')
        if status:
            if status == 'ACTIVE':
                queryset = queryset.filter(
                    is_active=True,
                    start_date__lte=date.today(),
                    end_date__gte=date.today()
                )
            elif status == 'INACTIVE':
                queryset = queryset.filter(is_active=False)
            elif status == 'COMPLETED':
                queryset = queryset.filter(
                    is_active=True,
                    end_date__lt=date.today()
                )
            elif status == 'EXCEEDED':
                # This requires a more complex filter that will be handled in the view
                # since it involves calculated fields
                pass
        
        # Date range filter
        start_date, end_date = self.get_date_range()
        if start_date and end_date:
            queryset = queryset.filter(
                start_date__lte=end_date,
                end_date__gte=start_date
            )
        
        return queryset


class BudgetDeleteConfirmationForm(forms.Form):
    """
    Confirmation form for budget deletion with safety checks.
    
    Provides:
    - Confirmation checkbox to prevent accidental deletions
    - Information about what will be deleted
    - Options for handling related data
    """
    
    confirm_deletion = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        }),
        label='Confirmo que desejo excluir este orçamento',
        help_text='Esta ação não pode ser desfeita. O orçamento será removido permanentemente.'
    )
    
    def __init__(self, budget, *args, **kwargs):
        """
        Initialize form with budget information.
        
        Args:
            budget: Budget instance to be deleted
        """
        self.budget = budget
        super().__init__(*args, **kwargs)
        
        # Add dynamic help text with budget information
        self.fields['confirm_deletion'].help_text = (
            f'Você está prestes a excluir o orçamento "{budget.name}" '
            f'(período: {budget.start_date.strftime("%d/%m/%Y")} a '
            f'{budget.end_date.strftime("%d/%m/%Y")}). '
            'Esta ação não pode ser desfeita.'
        )