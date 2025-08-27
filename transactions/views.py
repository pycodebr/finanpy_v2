from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, date
from decimal import Decimal
import logging

from .models import Transaction
from .forms import TransactionForm, TransactionFilterForm
from accounts.models import Account
from categories.models import Category

# Create logger for this module
logger = logging.getLogger(__name__)


class TransactionListView(LoginRequiredMixin, ListView):
    """
    List view for user transactions with filtering, searching, and pagination.
    
    Features:
    - User-scoped transaction listing
    - Date range, account, category, and type filtering
    - Description search functionality
    - Pagination (20 items per page)
    - Optimized queries with select_related
    - Order by date (most recent first)
    """
    
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        """Return user-scoped transactions with filters applied."""
        queryset = Transaction.objects.filter(user=self.request.user).select_related(
            'account', 'category'
        ).order_by('-transaction_date', '-created_at')
        
        # Apply filters from the filter form
        filter_form = TransactionFilterForm(
            user=self.request.user,
            data=self.request.GET
        )
        
        if filter_form.is_valid():
            # Apply standard filters
            filters = filter_form.get_filters()
            if filters:
                queryset = queryset.filter(**filters)
            
            # Apply search filter
            search_term = filter_form.get_search_term()
            if search_term:
                queryset = queryset.filter(
                    Q(description__icontains=search_term) |
                    Q(notes__icontains=search_term)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add filter form and summary statistics to context."""
        context = super().get_context_data(**kwargs)
        
        # Add filter form
        context['filter_form'] = TransactionFilterForm(
            user=self.request.user,
            data=self.request.GET
        )
        
        # Calculate summary statistics for filtered transactions
        transactions = self.get_queryset()
        
        income_total = sum(
            t.amount for t in transactions if t.transaction_type == 'INCOME'
        )
        expense_total = sum(
            t.amount for t in transactions if t.transaction_type == 'EXPENSE'
        )
        
        context.update({
            'total_transactions': transactions.count(),
            'income_total': income_total,
            'expense_total': expense_total,
            'balance': income_total - expense_total,
            'has_filters': bool(self.request.GET),
            'accounts_json': self._get_accounts_json(),
        })
        
        return context
    
    def _get_accounts_json(self):
        """Return JSON representation of user accounts."""
        import json
        
        accounts = []
        for account in Account.objects.filter(user=self.request.user, is_active=True):
            accounts.append({
                'id': account.id,
                'name': account.name,
                'type': account.get_account_type_display(),
                'balance': str(account.balance),
                'balance_display': account.balance_display,
            })
        
        return json.dumps(accounts)


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """
    Detail view for individual transactions.
    
    Features:
    - User-scoped access control
    - Related object information
    - Edit and delete action links
    """
    
    model = Transaction
    template_name = 'transactions/transaction_detail.html'
    context_object_name = 'transaction'
    
    def get_queryset(self):
        """Return user-scoped transactions with related objects."""
        return Transaction.objects.filter(user=self.request.user).select_related(
            'account', 'category'
        )


class TransactionCreateView(LoginRequiredMixin, CreateView):
    """
    Create view for new transactions.
    
    Features:
    - User-scoped form initialization
    - Dynamic category filtering by transaction type
    - Client-side currency formatting
    - Success messages and proper redirects
    - Validation with detailed error messages
    """
    
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:list')
    
    def get_form_kwargs(self):
        """Add user to form kwargs for user-scoped choices."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_initial(self):
        """Set default values for the form."""
        initial = super().get_initial()
        initial['transaction_date'] = date.today()
        
        # Pre-select account if provided in URL parameter
        account_id = self.request.GET.get('account')
        if account_id:
            try:
                # Ensure the account belongs to the current user
                from accounts.models import Account
                account = Account.objects.get(id=account_id, user=self.request.user)
                initial['account'] = account.id
            except (Account.DoesNotExist, ValueError):
                # Invalid account ID or doesn't belong to user, ignore
                pass
        
        return initial
    
    def form_valid(self, form):
        """Process valid form submission."""
        # Handle AJAX quick transaction requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                transaction = form.save(commit=False)
                transaction.user = self.request.user
                transaction.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Transação criada com sucesso!',
                    'transaction': {
                        'id': transaction.id,
                        'description': transaction.description,
                        'amount': str(transaction.amount),
                        'amount_display': transaction.amount_display,
                        'type': transaction.transaction_type,
                        'date': transaction.transaction_date.strftime('%d/%m/%Y')
                    }
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': 'Erro ao criar transação',
                    'errors': {'__all__': [str(e)]}
                }, status=400)
        
        # Set user before any form processing
        form.instance.user = self.request.user
        
        # Use the standard CreateView process but ensure user is set
        response = super().form_valid(form)
        
        # Add success message (transaction is now in self.object)
        try:
            transaction = self.object
            type_name = 'receita' if transaction.transaction_type == 'INCOME' else 'despesa'
            
            # Format amount in Brazilian currency format
            amount_formatted = f"R$ {float(transaction.amount):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            messages.success(
                self.request,
                f'Transação de {type_name} "{transaction.description}" '
                f'no valor de {amount_formatted} foi criada com sucesso!'
            )
        except Exception as e:
            # Fallback success message if there's an issue accessing transaction details
            messages.success(
                self.request,
                'Transação criada com sucesso!'
            )
        
        return response
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        # Handle AJAX quick transaction requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Dados do formulário inválidos',
                'errors': form.errors
            }, status=400)
        
        # Handle regular form submission
        messages.error(
            self.request,
            'Por favor, corrija os erros abaixo para criar a transação.'
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        context.update({
            'form_title': 'Nova Transação',
            'form_action': 'Criar',
            'categories_json': self._get_categories_json(),
        })
        return context
    
    def _get_categories_json(self):
        """Return JSON representation of user categories grouped by type."""
        import json
        
        categories = {}
        for category in Category.objects.filter(user=self.request.user, is_active=True):
            cat_type = category.category_type
            if cat_type not in categories:
                categories[cat_type] = []
            
            categories[cat_type].append({
                'id': category.id,
                'name': category.name,
                'full_path': category.full_path
            })
        
        return json.dumps(categories)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update view for existing transactions.
    
    Features:
    - User-scoped access control
    - Pre-populated form with current values
    - Audit trail logging
    - Success messages with change summary
    - Validation with detailed error messages
    """
    
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    
    def get_queryset(self):
        """Return user-scoped transactions."""
        return Transaction.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        """Add user to form kwargs for user-scoped choices."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        """Return success URL with option to go back to list or detail."""
        return reverse('transactions:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Process valid form submission with change logging."""
        # Store original values for change logging
        original = Transaction.objects.get(pk=self.object.pk)
        
        response = super().form_valid(form)
        
        # Log significant changes
        changes = self._get_changes(original, self.object)
        if changes:
            self._log_transaction_changes(original, changes)
        
        transaction = self.object
        type_name = 'receita' if transaction.transaction_type == 'INCOME' else 'despesa'
        
        messages.success(
            self.request,
            f'Transação de {type_name} "{transaction.description}" foi atualizada com sucesso!'
        )
        
        return response
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        messages.error(
            self.request,
            'Por favor, corrija os erros abaixo para atualizar a transação.'
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add additional context for template."""
        context = super().get_context_data(**kwargs)
        context.update({
            'form_title': f'Editar Transação',
            'form_action': 'Salvar',
            'categories_json': self._get_categories_json(),
        })
        return context
    
    def _get_categories_json(self):
        """Return JSON representation of user categories grouped by type."""
        import json
        
        categories = {}
        for category in Category.objects.filter(user=self.request.user, is_active=True):
            cat_type = category.category_type
            if cat_type not in categories:
                categories[cat_type] = []
            
            categories[cat_type].append({
                'id': category.id,
                'name': category.name,
                'full_path': category.full_path
            })
        
        return json.dumps(categories)
    
    def _get_changes(self, original, updated):
        """Compare original and updated transaction to identify changes."""
        changes = []
        
        fields_to_check = [
            ('transaction_type', 'Tipo'),
            ('account', 'Conta'),
            ('category', 'Categoria'),
            ('amount', 'Valor'),
            ('description', 'Descrição'),
            ('transaction_date', 'Data'),
            ('notes', 'Observações'),
            ('is_recurring', 'Recorrente'),
            ('recurrence_type', 'Tipo de Recorrência'),
        ]
        
        for field, label in fields_to_check:
            old_value = getattr(original, field)
            new_value = getattr(updated, field)
            
            if old_value != new_value:
                changes.append({
                    'field': label,
                    'old_value': str(old_value) if old_value else '-',
                    'new_value': str(new_value) if new_value else '-',
                })
        
        return changes
    
    def _log_transaction_changes(self, original, changes):
        """Log transaction changes for audit trail."""
        # This could be expanded to use Django's logging system
        # or store changes in a dedicated audit model
        import logging
        logger = logging.getLogger('transactions.audit')
        
        change_summary = ', '.join([
            f"{change['field']}: {change['old_value']} → {change['new_value']}"
            for change in changes
        ])
        
        logger.info(
            f'Transaction {original.id} updated by user {self.request.user.id}: {change_summary}'
        )


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete view for transactions with confirmation and audit logging.
    
    Features:
    - User-scoped access control
    - Confirmation page with transaction details
    - Success messages with deleted transaction info
    - Audit trail logging
    - Account balance adjustment via signals
    """
    
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transactions:list')
    context_object_name = 'transaction'
    
    def get_queryset(self):
        """Return user-scoped transactions."""
        return Transaction.objects.filter(user=self.request.user).select_related(
            'account', 'category'
        )
    
    def delete(self, request, *args, **kwargs):
        """Override delete to add success message and logging."""
        transaction = self.get_object()
        
        # Store transaction info before deletion for message and logging
        transaction_info = {
            'description': transaction.description,
            'amount': transaction.amount_display,
            'type': 'receita' if transaction.transaction_type == 'INCOME' else 'despesa',
            'date': transaction.transaction_date.strftime('%d/%m/%Y'),
        }
        
        # Log deletion for audit trail
        self._log_transaction_deletion(transaction)
        
        # Perform deletion
        response = super().delete(request, *args, **kwargs)
        
        # Add success message
        messages.success(
            request,
            f'Transação de {transaction_info["type"]} "{transaction_info["description"]}" '
            f'({transaction_info["amount"]}) foi excluída com sucesso!'
        )
        
        return response
    
    def _log_transaction_deletion(self, transaction):
        """Log transaction deletion for audit trail."""
        import logging
        logger = logging.getLogger('transactions.audit')
        
        logger.info(
            f'Transaction {transaction.id} deleted by user {self.request.user.id}: '
            f'{transaction.transaction_type} {transaction.amount} - {transaction.description}'
        )


def get_categories_by_type(request):
    """
    AJAX endpoint to return categories filtered by transaction type.
    
    Used for dynamic category filtering in transaction forms.
    
    Returns:
        JSON response with categories grouped by transaction type
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Get specific type if provided, otherwise return all types
    requested_type = request.GET.get('type')
    
    if requested_type and requested_type not in ['INCOME', 'EXPENSE']:
        return JsonResponse({'error': 'Invalid transaction type'}, status=400)
    
    # Build categories data structure
    categories_data = {}
    
    # Get categories for all types or specific type
    types_to_fetch = [requested_type] if requested_type else ['INCOME', 'EXPENSE']
    
    for transaction_type in types_to_fetch:
        categories = Category.objects.filter(
            user=request.user,
            category_type=transaction_type,
            is_active=True
        ).order_by('name')
        
        categories_data[transaction_type] = [
            {
                'id': category.id,
                'name': category.name,
                'full_path': category.full_path,
                'color': category.color,
                'icon': category.icon,
            }
            for category in categories
        ]
    
    # Return categories for specific type or all types
    if requested_type:
        return JsonResponse({'categories': categories_data[requested_type]})
    else:
        return JsonResponse(categories_data)


def get_accounts_data(request):
    """
    AJAX endpoint to return user's accounts data for quick transaction modal.
    
    Returns:
        JSON response with accounts information
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    accounts = Account.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('name')
    
    accounts_data = [
        {
            'id': account.id,
            'name': account.name,
            'type': account.get_account_type_display(),
            'balance': str(account.balance),
            'balance_display': account.balance_display,
        }
        for account in accounts
    ]
    
    return JsonResponse({'accounts': accounts_data})


# Additional utility views for enhanced functionality

class TransactionStatsView(LoginRequiredMixin, TemplateView):
    """
    Statistics view for transaction analysis.
    
    Provides detailed financial analytics and insights.
    """
    template_name = 'transactions/transaction_stats.html'
    
    def get(self, request, *args, **kwargs):
        """Handle GET request to show transaction statistics."""
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        """Calculate and return transaction statistics."""
        context = super().get_context_data(**kwargs)
        
        # Get user's transactions
        transactions = Transaction.objects.filter(user=self.request.user)
        
        # Calculate monthly summaries for the last 12 months
        monthly_data = []
        current_date = date.today()
        
        for i in range(12):
            year = current_date.year
            month = current_date.month - i
            
            if month <= 0:
                month += 12
                year -= 1
            
            summary = Transaction.get_monthly_summary(self.request.user, year, month)
            monthly_data.append({
                'year': year,
                'month': month,
                'month_name': date(year, month, 1).strftime('%B'),
                **summary
            })
        
        # Category breakdown
        from django.db.models import Sum
        
        category_income = transactions.filter(
            transaction_type='INCOME'
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')[:10]
        
        category_expenses = transactions.filter(
            transaction_type='EXPENSE'
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')[:10]
        
        # Account breakdown
        account_balances = []
        for account in Account.objects.filter(user=self.request.user, is_active=True):
            account_balances.append({
                'name': account.name,
                'balance': account.balance,
                'type': account.get_account_type_display(),
            })
        
        # Convert monthly_data to JSON-safe format
        import json
        monthly_data_json = []
        for item in reversed(monthly_data):
            monthly_data_json.append({
                'year': item['year'],
                'month': item['month'],
                'month_name': item['month_name'],
                'income': float(item['income']),
                'expenses': float(item['expenses']),
                'balance': float(item['balance']),
                'transaction_count': item['transaction_count']
            })
        
        context.update({
            'monthly_data': list(reversed(monthly_data)),
            'monthly_data_json': json.dumps(monthly_data_json),
            'category_income': category_income,
            'category_expenses': category_expenses,
            'account_balances': account_balances,
        })
        
        return context
