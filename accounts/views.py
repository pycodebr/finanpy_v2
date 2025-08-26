from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)
from django.db.models import Q, Sum, Count
from django.http import Http404
from decimal import Decimal

from .models import Account
from .forms import AccountForm, AccountFilterForm


class AccountListView(LoginRequiredMixin, ListView):
    """
    Display a list of user's accounts with filtering capabilities.
    
    Shows account information including balances, types, and provides
    filtering options. Includes summary statistics for user's accounts.
    """
    model = Account
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'
    paginate_by = 20
    
    def get_queryset(self):
        """Return user-scoped queryset with optional filtering."""
        queryset = Account.objects.filter(user=self.request.user)
        
        # Apply filters from form
        form = AccountFilterForm(self.request.GET)
        if form.is_valid():
            account_type = form.cleaned_data.get('account_type')
            currency = form.cleaned_data.get('currency')
            status = form.cleaned_data.get('status')
            
            if account_type:
                queryset = queryset.filter(account_type=account_type)
            
            if currency:
                queryset = queryset.filter(currency=currency)
            
            if status == 'active':
                queryset = queryset.filter(is_active=True)
            elif status == 'inactive':
                queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        
        # Add filter form
        context['filter_form'] = AccountFilterForm(self.request.GET)
        
        # Calculate summary statistics
        user_accounts = Account.objects.filter(user=self.request.user)
        
        # Group by currency for summary
        currency_summaries = {}
        for currency_code, currency_name in Account.CURRENCY_CHOICES:
            accounts_in_currency = user_accounts.filter(
                currency=currency_code, is_active=True
            )
            if accounts_in_currency.exists():
                total_balance = accounts_in_currency.aggregate(
                    total=Sum('balance')
                )['total'] or Decimal('0.00')
                
                currency_summaries[currency_code] = {
                    'name': currency_name,
                    'total_balance': total_balance,
                    'account_count': accounts_in_currency.count(),
                }
        
        context['currency_summaries'] = currency_summaries
        
        # Overall statistics
        context['total_accounts'] = user_accounts.count()
        context['active_accounts'] = user_accounts.filter(is_active=True).count()
        context['inactive_accounts'] = user_accounts.filter(is_active=False).count()
        
        return context


class AccountDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed information about a single account.
    
    Shows account details and recent transaction history (when implemented).
    """
    model = Account
    template_name = 'accounts/account_detail.html'
    context_object_name = 'account'
    
    def get_queryset(self):
        """Ensure user can only access their own accounts."""
        return Account.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        
        # Add account statistics
        account = self.get_object()
        context['is_debt_account'] = account.is_debt_account
        
        # Future: Add recent transactions when Transaction model is implemented
        # context['recent_transactions'] = account.get_transactions_queryset()[:10]
        
        return context


class AccountCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new account for the authenticated user.
    
    Uses AccountForm with custom validation and user assignment.
    """
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:account-list')
    
    def get_form_kwargs(self):
        """Pass current user to form for validation."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Set user and display success message."""
        form.instance.user = self.request.user
        
        messages.success(
            self.request,
            f'Conta "{form.instance.name}" foi criada com sucesso!'
        )
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Criar Nova Conta'
        context['submit_text'] = 'Criar Conta'
        return context


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing account.
    
    Ensures user can only edit their own accounts with proper validation.
    """
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    
    def get_queryset(self):
        """Ensure user can only edit their own accounts."""
        return Account.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        """Pass current user to form for validation."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        """Redirect to account detail after successful update."""
        return reverse('accounts:account-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Display success message."""
        messages.success(
            self.request,
            f'Conta "{form.instance.name}" foi atualizada com sucesso!'
        )
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Editar Conta: {self.object.name}'
        context['submit_text'] = 'Atualizar Conta'
        return context


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    """
    Soft delete an account (set is_active=False).
    
    Provides confirmation page and preserves data for audit purposes.
    Uses soft delete to maintain transaction history integrity.
    """
    model = Account
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('accounts:account-list')
    
    def get_queryset(self):
        """Ensure user can only delete their own accounts."""
        return Account.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Perform soft delete instead of actual deletion."""
        self.object = self.get_object()
        
        # Check if account has transactions (when Transaction model is implemented)
        # This is a safeguard to prevent data loss
        # has_transactions = self.object.transactions.exists()
        has_transactions = False  # Placeholder until Transaction model exists
        
        if has_transactions:
            # Soft delete to preserve transaction history
            self.object.is_active = False
            self.object.save()
            
            messages.warning(
                request,
                f'Account "{self.object.name}" has been deactivated. '
                f'It still appears in reports but won\'t be used for new transactions.'
            )
        else:
            # Safe to actually delete if no transactions
            account_name = self.object.name
            self.object.delete()
            
            messages.success(
                request,
                f'Conta "{account_name}" foi excluída com sucesso.'
            )
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        """Add context for confirmation template."""
        context = super().get_context_data(**kwargs)
        
        # Future: Check for related data when other models are implemented
        context['has_transactions'] = False  # Placeholder
        context['deletion_type'] = 'deactivation' if context['has_transactions'] else 'permanent'
        
        return context


# Utility views for AJAX operations (future enhancement)
class AccountBalanceUpdateView(LoginRequiredMixin, UpdateView):
    """
    Quick balance update view for AJAX operations.
    
    This is a utility view that can be used for quick balance updates
    without full form processing, useful for dashboard interactions.
    """
    model = Account
    fields = ['balance']
    http_method_names = ['post']
    
    def get_queryset(self):
        """Ensure user can only update their own accounts."""
        return Account.objects.filter(user=self.request.user, is_active=True)
    
    def form_valid(self, form):
        """Return JSON response for AJAX."""
        from django.http import JsonResponse
        
        account = form.save()
        
        return JsonResponse({
            'success': True,
            'new_balance': str(account.balance),
            'formatted_balance': account.balance_display,
            'account_name': account.name,
        })
    
    def form_invalid(self, form):
        """Return error response for AJAX."""
        from django.http import JsonResponse
        
        return JsonResponse({
            'success': False,
            'errors': form.errors,
        }, status=400)
