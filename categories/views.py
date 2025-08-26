"""
Views for category management with hierarchical support.

This module provides CRUD operations for categories with user-scoped data access,
hierarchical display, and proper validation for maintaining data integrity.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q, Count, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)

from .models import Category
from .forms import CategoryForm, CategoryFilterForm, CategoryBulkActionForm


class CategoryListView(LoginRequiredMixin, ListView):
    """
    List view for categories with hierarchical display and filtering.
    
    Features:
    - Hierarchical tree display with visual indentation
    - User-scoped data access
    - Filtering by type and active status
    - Search functionality
    - Bulk actions for category management
    """
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'
    paginate_by = 50
    
    def get_queryset(self):
        """Get user's categories with hierarchical ordering and filtering."""
        queryset = Category.objects.filter(user=self.request.user)
        
        # Apply filters from form
        filter_form = CategoryFilterForm(self.request.GET)
        
        if filter_form.is_valid():
            # Filter by category type
            category_type = filter_form.cleaned_data.get('category_type')
            if category_type:
                queryset = queryset.filter(category_type=category_type)
            
            # Filter by active status
            status = filter_form.cleaned_data.get('status')
            if status == 'active':
                queryset = queryset.filter(is_active=True)
            elif status == 'inactive':
                queryset = queryset.filter(is_active=False)
            
            # Filter by search term
            search = filter_form.cleaned_data.get('search')
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(parent__name__icontains=search)
                )
        
        # Add transaction count annotation
        # from transactions.models import Transaction  # TODO: Will be implemented in Sprint 3
        queryset = queryset.annotate(
            # transaction_count=Count('transactions'),  # TODO: Enable in Sprint 3
            has_children=Exists(
                Category.objects.filter(parent=OuterRef('pk'))
            )
        )
        
        # Order for hierarchical display
        return self._get_hierarchical_queryset(queryset)
    
    def _get_hierarchical_queryset(self, queryset):
        """
        Order categories in hierarchical structure.
        
        Returns a list of categories ordered to show parent-child relationships
        with proper indentation levels.
        """
        categories = list(queryset.select_related('parent'))
        
        # Group categories by type for separate hierarchies
        income_categories = [c for c in categories if c.category_type == 'INCOME']
        expense_categories = [c for c in categories if c.category_type == 'EXPENSE']
        
        # Build hierarchical order for each type
        ordered_categories = []
        
        if income_categories:
            ordered_categories.extend(
                self._build_hierarchy_order(income_categories)
            )
        
        if expense_categories:
            ordered_categories.extend(
                self._build_hierarchy_order(expense_categories)
            )
        
        return ordered_categories
    
    def _build_hierarchy_order(self, categories):
        """Build hierarchical order for a list of categories."""
        # Create category dict for quick lookup
        category_dict = {cat.id: cat for cat in categories}
        
        # Find root categories and build tree
        root_categories = [cat for cat in categories if cat.parent_id is None]
        root_categories.sort(key=lambda x: x.name)
        
        ordered = []
        
        def add_category_and_children(category, level=0):
            # Set display level for template
            category.display_level = level
            ordered.append(category)
            
            # Find and add children
            children = [
                cat for cat in categories 
                if cat.parent_id == category.id
            ]
            children.sort(key=lambda x: x.name)
            
            for child in children:
                add_category_and_children(child, level + 1)
        
        # Build ordered list starting from roots
        for root in root_categories:
            add_category_and_children(root)
        
        # Add orphaned categories (shouldn't happen with proper data)
        added_ids = {cat.id for cat in ordered}
        orphaned = [cat for cat in categories if cat.id not in added_ids]
        
        for orphan in orphaned:
            orphan.display_level = 0
            ordered.append(orphan)
        
        return ordered
    
    def get_context_data(self, **kwargs):
        """Add filter form and statistics to context."""
        context = super().get_context_data(**kwargs)
        
        # Add filter form
        context['filter_form'] = CategoryFilterForm(self.request.GET)
        
        # Add bulk action form
        context['bulk_form'] = CategoryBulkActionForm(user=self.request.user)
        
        # Add category statistics
        user_categories = Category.objects.filter(user=self.request.user)
        context['stats'] = {
            'total_categories': user_categories.count(),
            'income_categories': user_categories.filter(
                category_type='INCOME'
            ).count(),
            'expense_categories': user_categories.filter(
                category_type='EXPENSE'
            ).count(),
            'active_categories': user_categories.filter(is_active=True).count(),
            'inactive_categories': user_categories.filter(is_active=False).count(),
        }
        
        return context


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create view for new categories with parent selection."""
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('categories:category-list')
    success_message = 'Categoria "%(name)s" criada com sucesso!'
    
    def get_form_kwargs(self):
        """Pass user to form for parent filtering."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add context for create view."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Nova Categoria'
        context['form_title'] = 'Criar Nova Categoria'
        context['submit_text'] = 'Criar Categoria'
        context['cancel_url'] = reverse_lazy('categories:category-list')
        
        # Add available parents for JavaScript filtering
        context['parent_categories'] = self._get_parent_categories_json()
        
        return context
    
    def _get_parent_categories_json(self):
        """Get parent categories grouped by type for JavaScript filtering."""
        user_categories = Category.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('parent').order_by('category_type', 'name')
        
        categories_by_type = {}
        
        for category in user_categories:
            type_key = category.category_type
            if type_key not in categories_by_type:
                categories_by_type[type_key] = []
            
            categories_by_type[type_key].append({
                'id': category.id,
                'name': category.name,
                'full_path': category.full_path,
                'level': category.level,
            })
        
        return categories_by_type


class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update view for existing categories with hierarchy validation."""
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('categories:category-list')
    success_message = 'Categoria "%(name)s" atualizada com sucesso!'
    
    def get_queryset(self):
        """Ensure user can only edit their own categories."""
        return Category.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        """Pass user to form for parent filtering."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add context for update view."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Editar {self.object.name}'
        context['form_title'] = f'Editar Categoria: {self.object.name}'
        context['submit_text'] = 'Salvar Alterações'
        context['cancel_url'] = reverse_lazy('categories:category-list')
        
        # Add available parents (excluding self and descendants)
        context['parent_categories'] = self._get_parent_categories_json()
        
        # Add category descendants for validation warnings
        context['descendants'] = list(
            self.object.get_descendants().values_list('name', flat=True)
        )
        
        return context
    
    def _get_parent_categories_json(self):
        """Get valid parent categories for this category."""
        # Get all user categories except self and descendants
        descendants_ids = list(
            self.object.get_descendants().values_list('id', flat=True)
        )
        excluded_ids = descendants_ids + [self.object.id]
        
        user_categories = Category.objects.filter(
            user=self.request.user,
            category_type=self.object.category_type,
            is_active=True
        ).exclude(id__in=excluded_ids).select_related('parent').order_by('name')
        
        categories = []
        for category in user_categories:
            categories.append({
                'id': category.id,
                'name': category.name,
                'full_path': category.full_path,
                'level': category.level,
            })
        
        return {self.object.category_type: categories}


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for categories with dependency checking."""
    model = Category
    template_name = 'categories/category_confirm_delete.html'
    success_url = reverse_lazy('categories:category-list')
    
    def get_queryset(self):
        """Ensure user can only delete their own categories."""
        return Category.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Add dependency information to context."""
        context = super().get_context_data(**kwargs)
        
        # Check for dependencies
        children = self.object.children.all()
        
        # TODO: Enable transaction checking in Sprint 3
        # Check for transactions (when transactions app is implemented)
        transaction_count = 0
        # try:
        #     transaction_count = self.object.transactions.count()
        # except AttributeError:
        #     # Transactions model not yet related
        #     pass
        
        context.update({
            'has_children': children.exists(),
            'children': children,
            'transaction_count': transaction_count,
            'can_delete': not children.exists() and transaction_count == 0,
        })
        
        return context
    
    def delete(self, request, *args, **kwargs):
        """Override delete to check dependencies and handle soft delete."""
        self.object = self.get_object()
        
        # Check for child categories
        if self.object.children.exists():
            messages.error(
                request,
                f'Não é possível excluir a categoria "{self.object.name}" '
                'porque ela possui subcategorias. Exclua as subcategorias primeiro.'
            )
            return redirect('categories:category-list')
        
        # TODO: Enable transaction checking in Sprint 3
        # Check for transactions
        transaction_count = 0
        # try:
        #     transaction_count = self.object.transactions.count()
        # except AttributeError:
        #     pass
        
        if transaction_count > 0:
            # Soft delete by deactivating instead of actual deletion
            self.object.is_active = False
            self.object.save()
            messages.warning(
                request,
                f'A categoria "{self.object.name}" foi desativada porque '
                f'possui {transaction_count} transação(ões) associada(s). '
                'Para reativá-la, acesse a lista de categorias.'
            )
        else:
            # Safe to delete
            category_name = self.object.name
            self.object.delete()
            messages.success(
                request,
                f'Categoria "{category_name}" excluída com sucesso!'
            )
        
        return redirect(self.success_url)


class CategoryDetailView(LoginRequiredMixin, DetailView):
    """Detail view for categories with hierarchy and usage information."""
    model = Category
    template_name = 'categories/category_detail.html'
    context_object_name = 'category'
    
    def get_queryset(self):
        """Ensure user can only view their own categories."""
        return Category.objects.filter(user=self.request.user).select_related(
            'parent'
        ).prefetch_related('children')
    
    def get_context_data(self, **kwargs):
        """Add hierarchy and usage information."""
        context = super().get_context_data(**kwargs)
        
        # Add hierarchy information
        context['ancestors'] = self.object.get_ancestors()
        context['descendants'] = self.object.get_descendants()
        context['siblings'] = self.object.get_siblings()
        
        # TODO: Add usage statistics in Sprint 3
        # Add usage statistics
        transaction_count = 0
        # try:
        #     transaction_count = self.object.transactions.count()
        # except AttributeError:
        #     pass
        
        context['transaction_count'] = transaction_count
        
        return context


def get_parent_categories_ajax(request):
    """
    AJAX view to get parent categories filtered by type.
    
    Returns JSON response with categories of the specified type for
    dynamic parent selection in forms.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    category_type = request.GET.get('type')
    exclude_id = request.GET.get('exclude')
    
    if not category_type:
        return JsonResponse({'error': 'Type parameter required'}, status=400)
    
    # Build queryset
    queryset = Category.objects.filter(
        user=request.user,
        category_type=category_type,
        is_active=True
    )
    
    # Exclude specific category and its descendants (for edit forms)
    if exclude_id:
        try:
            exclude_category = Category.objects.get(
                id=exclude_id,
                user=request.user
            )
            descendants_ids = list(
                exclude_category.get_descendants().values_list('id', flat=True)
            )
            exclude_ids = descendants_ids + [int(exclude_id)]
            queryset = queryset.exclude(id__in=exclude_ids)
        except (Category.DoesNotExist, ValueError):
            pass
    
    # Build response data
    categories = []
    for category in queryset.select_related('parent').order_by('name'):
        categories.append({
            'id': category.id,
            'name': category.name,
            'full_path': category.full_path,
            'level': category.level,
        })
    
    return JsonResponse({'categories': categories})


def bulk_category_action(request):
    """
    Handle bulk actions on categories.
    
    Supports activating/deactivating multiple categories at once.
    """
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    if request.method == 'POST':
        form = CategoryBulkActionForm(request.POST, user=request.user)
        
        if form.is_valid():
            action = form.cleaned_data['action']
            categories = form.cleaned_data['selected_categories']
            
            if action == 'activate':
                categories.update(is_active=True)
                count = categories.count()
                messages.success(
                    request,
                    f'{count} categoria(s) ativada(s) com sucesso!'
                )
            elif action == 'deactivate':
                categories.update(is_active=False)
                count = categories.count()
                messages.success(
                    request,
                    f'{count} categoria(s) desativada(s) com sucesso!'
                )
        else:
            messages.error(
                request,
                'Erro ao executar ação em lote. Verifique os dados enviados.'
            )
    
    return redirect('categories:category-list')
