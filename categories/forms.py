"""
Forms for category management with hierarchical support.

This module provides forms for creating and editing categories with dynamic parent
selection based on category type and user ownership, along with custom validation
for hierarchy integrity.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Category


class CategoryForm(forms.ModelForm):
    """
    Form for creating and editing categories with dynamic parent selection.
    
    Features:
    - Dynamic parent queryset filtering by category type and user
    - Hierarchy loop validation
    - Custom field widgets with enhanced styling
    - User-friendly error messages
    """
    
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'parent', 'color', 'icon', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Digite o nome da categoria',
                'maxlength': '50',
            }),
            'category_type': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'updateParentOptions(this.value)',
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_parent',
            }),
            'color': forms.Select(attrs={
                'class': 'form-select color-picker',
                'onchange': 'updateColorPreview(this.value)',
            }),
            'icon': forms.Select(attrs={
                'class': 'form-select icon-picker',
                'onchange': 'updateIconPreview(this.value)',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }
        labels = {
            'name': 'Nome da Categoria',
            'category_type': 'Tipo de Categoria',
            'parent': 'Categoria Pai (opcional)',
            'color': 'Cor',
            'icon': 'Ícone',
            'is_active': 'Categoria Ativa',
        }
        help_texts = {
            'name': 'Nome único para identificar esta categoria',
            'category_type': 'Selecione se esta categoria é para receitas ou despesas',
            'parent': 'Categoria pai para organização hierárquica (opcional)',
            'color': 'Cor para identificação visual da categoria',
            'icon': 'Ícone emoji para representar a categoria',
            'is_active': 'Desmarque para desativar esta categoria',
        }
    
    def __init__(self, *args, user=None, **kwargs):
        """
        Initialize form with user-specific parent options.
        
        Args:
            user: User instance for filtering parent categories
        """
        self.user = user
        super().__init__(*args, **kwargs)
        
        # Set user on the instance for model validation
        if self.user and self.instance:
            self.instance.user = self.user
        
        # Filter parent queryset by user and add empty option
        if self.user:
            self.fields['parent'].queryset = Category.objects.filter(
                user=self.user, is_active=True
            ).order_by('category_type', 'name')
            self.fields['parent'].empty_label = "Nenhuma (categoria raiz)"
        
        # If editing existing category, filter parents by same type
        if self.instance and self.instance.pk:
            self._filter_parent_by_category_type()
    
    def _filter_parent_by_category_type(self):
        """Filter parent options based on current category type."""
        if self.instance.category_type:
            self.fields['parent'].queryset = self.fields['parent'].queryset.filter(
                category_type=self.instance.category_type
            ).exclude(id=self.instance.id)
    
    def clean_name(self):
        """Validate category name."""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise ValidationError('O nome da categoria não pode estar vazio.')
        
        # Check for uniqueness within user and category type
        user = self.user
        category_type = self.cleaned_data.get('category_type')
        
        if not user or not category_type:
            return name
        
        # Build queryset for uniqueness check
        existing_query = Category.objects.filter(
            user=user,
            name__iexact=name,
            category_type=category_type
        )
        
        # Exclude current instance if editing
        if self.instance and self.instance.pk:
            existing_query = existing_query.exclude(pk=self.instance.pk)
        
        if existing_query.exists():
            raise ValidationError(
                f'Já existe uma categoria {category_type.lower()} '
                f'com o nome "{name}". Escolha um nome diferente.'
            )
        
        return name
    
    def clean_parent(self):
        """Validate parent selection to prevent hierarchy loops."""
        parent = self.cleaned_data.get('parent')
        category_type = self.cleaned_data.get('category_type')
        
        if not parent:
            return parent
        
        # Validate parent belongs to same user (additional safety check)
        if self.user and parent.user != self.user:
            raise ValidationError('A categoria pai deve pertencer ao mesmo usuário.')
        
        # Validate parent has same category type
        if category_type and parent.category_type != category_type:
            raise ValidationError(
                'A categoria pai deve ser do mesmo tipo '
                f'({category_type.lower()}).'
            )
        
        # Validate no circular reference
        if self.instance and self.instance.pk:
            if parent == self.instance:
                raise ValidationError('Uma categoria não pode ser pai de si mesma.')
            
            # Check if parent is descendant of current category
            current = parent
            visited = set()
            
            while current and current.id not in visited:
                if current.id == self.instance.id:
                    raise ValidationError(
                        'Esta seleção criaria uma referência circular. '
                        'A categoria pai não pode ser uma subcategoria desta categoria.'
                    )
                visited.add(current.id)
                current = current.parent
        
        return parent
    
    def clean(self):
        """Perform cross-field validation."""
        cleaned_data = super().clean()
        
        # Set user on instance for model validation
        if self.user:
            self.instance.user = self.user
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save category with user assignment."""
        category = super().save(commit=False)
        
        # Assign user if provided
        if self.user and not category.user_id:
            category.user = self.user
        
        if commit:
            category.save()
        
        return category


class CategoryFilterForm(forms.Form):
    """
    Form for filtering categories in list view.
    
    Provides filters for category type and active status.
    """
    
    CATEGORY_TYPE_CHOICES = [
        ('', 'Todos os Tipos'),
        ('INCOME', 'Receitas'),
        ('EXPENSE', 'Despesas'),
    ]
    
    ACTIVE_STATUS_CHOICES = [
        ('', 'Todas'),
        ('active', 'Ativas'),
        ('inactive', 'Inativas'),
    ]
    
    category_type = forms.ChoiceField(
        choices=CATEGORY_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'onchange': 'this.form.submit()',
        }),
        label='Tipo'
    )
    
    status = forms.ChoiceField(
        choices=ACTIVE_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'onchange': 'this.form.submit()',
        }),
        label='Status'
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input form-input-sm',
            'placeholder': 'Buscar por nome...',
        }),
        label='Buscar'
    )


class CategoryBulkActionForm(forms.Form):
    """
    Form for bulk actions on multiple categories.
    
    Allows deactivating/activating multiple categories at once.
    """
    
    ACTION_CHOICES = [
        ('', 'Selecione uma ação'),
        ('activate', 'Ativar selecionadas'),
        ('deactivate', 'Desativar selecionadas'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Ação'
    )
    
    selected_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.none(),
        widget=forms.MultipleHiddenInput(),
        required=True
    )
    
    def __init__(self, *args, user=None, **kwargs):
        """Initialize form with user-scoped category queryset."""
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['selected_categories'].queryset = Category.objects.filter(
                user=user
            )
    
    def clean_action(self):
        """Validate that a valid action is selected."""
        action = self.cleaned_data.get('action')
        
        if not action:
            raise ValidationError('Selecione uma ação para executar.')
        
        return action
    
    def clean_selected_categories(self):
        """Validate that categories are selected."""
        categories = self.cleaned_data.get('selected_categories')
        
        if not categories:
            raise ValidationError('Selecione pelo menos uma categoria.')
        
        return categories