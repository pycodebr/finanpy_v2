from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

User = get_user_model()


class Category(models.Model):
    """
    Category model for organizing financial transactions hierarchically.
    
    This model supports hierarchical categorization of income and expenses, allowing users
    to create main categories and subcategories for detailed financial organization.
    Each category is user-scoped for data isolation and supports customization with colors and icons.
    
    Schema from PRD:
    - ForeignKey to User for data isolation
    - Name and category type (INCOME/EXPENSE)
    - Visual customization (color and icon)
    - Self-referencing FK for hierarchical organization
    - Active/inactive status for category lifecycle
    - Timestamps for audit trail
    
    Features:
    - Hierarchical organization (parent/child relationships)
    - Loop prevention in hierarchy
    - Visual customization for UI consistency
    - User-scoped data isolation
    - Efficient querying with proper indexing
    """
    
    # Category type choices for income vs expense classification
    CATEGORY_TYPE_CHOICES = [
        ('INCOME', 'Receita'),
        ('EXPENSE', 'Despesa'),
    ]
    
    # Predefined color choices for UI consistency
    COLOR_CHOICES = [
        ('#10B981', 'Verde'),      # emerald-500
        ('#3B82F6', 'Azul'),       # blue-500
        ('#8B5CF6', 'Roxo'),       # violet-500
        ('#F59E0B', 'Amarelo'),    # amber-500
        ('#EF4444', 'Vermelho'),   # red-500
        ('#06B6D4', 'Ciano'),      # cyan-500
        ('#84CC16', 'Lima'),       # lime-500
        ('#F97316', 'Laranja'),    # orange-500
        ('#EC4899', 'Rosa'),       # pink-500
        ('#6B7280', 'Cinza'),      # gray-500
    ]
    
    # Common icon choices for financial categories
    ICON_CHOICES = [
        ('💰', 'Saco de Dinheiro'),
        ('💳', 'Cartão de Crédito'),
        ('🏠', 'Casa'),
        ('🚗', 'Carro'),
        ('🍔', 'Comida'),
        ('⚡', 'Utilidades'),
        ('🎬', 'Entretenimento'),
        ('👔', 'Trabalho'),
        ('🏥', 'Saúde'),
        ('🎓', 'Educação'),
        ('✈️', 'Viagem'),
        ('🛍️', 'Compras'),
        ('💊', 'Farmácia'),
        ('⛽', 'Combustível'),
        ('📱', 'Tecnologia'),
        ('🎁', 'Presentes'),
        ('🏃', 'Esportes'),
        ('📊', 'Investimento'),
        ('🔧', 'Manutenção'),
        ('📚', 'Livros'),
    ]
    
    # Color hex validator
    color_validator = RegexValidator(
        regex=r'^#[0-9A-Fa-f]{6}$',
        message='Color must be a valid hex color code (e.g., #10B981)'
    )
    
    # Core fields following PRD schema
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories',
        help_text='Owner of this category'
    )
    
    name = models.CharField(
        max_length=50,
        verbose_name='Nome',
        help_text='Nome da categoria (ex.: "Alimentação", "Transporte", "Salário")'
    )
    
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES,
        verbose_name='Tipo',
        help_text='Se esta categoria é para receitas ou despesas'
    )
    
    color = models.CharField(
        max_length=7,
        choices=COLOR_CHOICES,
        default='#6B7280',
        validators=[color_validator],
        verbose_name='Cor',
        help_text='Código hexadecimal da cor para identificação visual'
    )
    
    icon = models.CharField(
        max_length=10,
        choices=ICON_CHOICES,
        default='💰',
        verbose_name='Ícone',
        help_text='Ícone emoji para identificação visual'
    )
    
    # Self-referencing foreign key for hierarchical categories
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Categoria Pai',
        help_text='Categoria pai para organização hierárquica'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativa',
        help_text='Se esta categoria está ativa e disponível para uso'
    )
    
    # Timestamps for audit trail
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em',
        help_text='Quando esta categoria foi criada'
    )
    
    class Meta:
        ordering = ['category_type', 'name']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        # Ensure unique category names per user and type
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name', 'category_type'],
                name='unique_category_name_per_user_type'
            )
        ]
        # Add indexes for common queries
        indexes = [
            models.Index(fields=['user', 'category_type', 'is_active']),
            models.Index(fields=['user', 'parent']),
            models.Index(fields=['category_type', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        """Return string representation with hierarchy path."""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def clean(self):
        """Perform model-level validation."""
        super().clean()
        
        # Validate category name is not empty after stripping whitespace
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Category name cannot be empty.'})
        
        # Clean the name by stripping whitespace and title casing
        self.name = self.name.strip()
        
        # Validate parent relationship doesn't create loops
        if self.parent:
            self._validate_no_hierarchy_loops()
            
            # Ensure parent is same user and category type
            if self.parent.user != self.user:
                raise ValidationError({
                    'parent': 'Parent category must belong to the same user.'
                })
            
            if self.parent.category_type != self.category_type:
                raise ValidationError({
                    'parent': 'Parent category must be of the same type (Income/Expense).'
                })
    
    def save(self, *args, **kwargs):
        """Override save to ensure clean() validation is called."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def _validate_no_hierarchy_loops(self):
        """Validate that parent relationship doesn't create infinite loops."""
        if not self.parent:
            return
        
        # Check if we're trying to set ourselves as parent
        if self.parent == self:
            raise ValidationError({
                'parent': 'A category cannot be its own parent.'
            })
        
        # Check for circular references by traversing up the hierarchy
        current = self.parent
        visited = set()
        
        while current:
            if current.id == self.id:
                raise ValidationError({
                    'parent': 'This parent selection would create a circular reference.'
                })
            
            if current.id in visited:
                # This shouldn't happen with proper data, but prevents infinite loops
                break
                
            visited.add(current.id)
            current = current.parent
    
    @property
    def full_path(self):
        """Return the full hierarchical path of this category."""
        path = []
        current = self
        
        while current:
            path.insert(0, current.name)
            current = current.parent
        
        return ' > '.join(path)
    
    @property
    def level(self):
        """Return the depth level in the hierarchy (0 for root categories)."""
        level = 0
        current = self.parent
        
        while current:
            level += 1
            current = current.parent
            
        return level
    
    @property
    def is_root(self):
        """Return True if this is a root category (has no parent)."""
        return self.parent is None
    
    @property
    def is_leaf(self):
        """Return True if this is a leaf category (has no children)."""
        return not self.children.exists()
    
    def get_ancestors(self):
        """Return queryset of all ancestor categories (parents, grandparents, etc.)."""
        ancestors = []
        current = self.parent
        
        while current:
            ancestors.append(current.id)
            current = current.parent
        
        return Category.objects.filter(id__in=ancestors).order_by('name')
    
    def get_descendants(self):
        """Return queryset of all descendant categories (children, grandchildren, etc.)."""
        descendants = []
        
        def collect_descendants(category):
            for child in category.children.all():
                descendants.append(child.id)
                collect_descendants(child)
        
        collect_descendants(self)
        return Category.objects.filter(id__in=descendants).order_by('name')
    
    def get_root(self):
        """Return the root category of this hierarchy."""
        current = self
        
        while current.parent:
            current = current.parent
            
        return current
    
    def get_siblings(self):
        """Return queryset of sibling categories (same parent)."""
        if self.parent:
            return self.parent.children.exclude(id=self.id)
        else:
            # Root level siblings
            return Category.objects.filter(
                user=self.user,
                category_type=self.category_type,
                parent__isnull=True
            ).exclude(id=self.id)
    
    @classmethod
    def get_user_tree(cls, user, category_type=None):
        """
        Return hierarchical tree structure of categories for a user.
        
        Args:
            user: User object
            category_type: Optional filter by INCOME or EXPENSE
            
        Returns:
            QuerySet of root categories with prefetched children
        """
        queryset = cls.objects.filter(user=user, is_active=True)
        
        if category_type:
            queryset = queryset.filter(category_type=category_type)
        
        # Get root categories and prefetch their children
        return queryset.filter(parent__isnull=True).prefetch_related('children')
    
    def can_have_transactions(self):
        """
        Return True if this category can have transactions assigned to it.
        
        By default, all categories can have transactions, but this method
        can be extended with business logic if needed (e.g., only leaf categories).
        """
        return self.is_active
