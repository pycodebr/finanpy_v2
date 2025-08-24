# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Finanpy is a personal financial management web system built with Django 5.2+ and Python 3.13+. It enables users to manage bank accounts, track transactions, create budgets, set financial goals, and visualize financial data through reports and charts.

The system follows a modular architecture with separate Django apps for each domain:
- `users` - Authentication and user management  
- `profiles` - User profiles and personal information
- `accounts` - Bank accounts and cards management
- `categories` - Transaction categorization (with hierarchical support)
- `transactions` - Financial transactions (income/expenses)
- `budgets` - Budget planning and tracking
- `goals` - Financial goals and savings targets

**Important**: Django signals should be placed in a `signals.py` file within the corresponding app directory, not in models.py. For example, account balance update signals go in `accounts/signals.py`.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Database Operations
```bash
# Create migrations for all apps
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development Server
```bash
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8001
```

### Static Files Management
```bash
# Collect static files (production)
python manage.py collectstatic

# Find static files location
python manage.py findstatic css/custom.css

# Auto-collect during development (already configured)
python manage.py runserver  # Serves static files automatically
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts

# Run single test method
python manage.py test accounts.tests.TestAccountModel.test_balance_update

# Run tests with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Database Utilities
```bash
# Django shell with auto-imported models
pip install django-extensions
python manage.py shell_plus

# Check for issues
python manage.py check

# View migration status
python manage.py showmigrations
```

## Architecture Overview

The system follows Django's MVT (Model-View-Template) pattern with these key architectural decisions:

### Data Model Relationships
- All models are user-scoped (foreign key to User)
- Categories support hierarchical organization (self-referencing FK)
- Transactions link User, Account, and Category
- Account balances are automatically updated via Django signals
- Budget spent amounts are calculated from related transactions

### View Architecture
- Primarily uses Django Class-Based Views (CBV)
- All views require authentication (LoginRequiredMixin)
- User-scoped querysets ensure data isolation
- Optimized queries using select_related/prefetch_related

### Frontend Architecture
- **Base Template**: `templates/base.html` with TailwindCSS via CDN and dark theme
- **Custom Styles**: `static/css/custom.css` with financial-specific components (.card, .btn-primary, form inputs)
- **JavaScript**: `static/js/main.js` with utilities for currency formatting, theme management, and Chart.js integration
- **Design System**: Dark theme with custom gradients (primary, success, danger, warning colors)
- **Responsive**: Mobile-first approach using TailwindCSS breakpoints

### Key Domain Logic
- **Account Balance Updates**: Django signals in `accounts/signals.py` automatically adjust account balances when transactions are created/deleted
- **Budget Tracking**: Budgets calculate spent amounts by aggregating related transactions within date ranges
- **Category Hierarchy**: Categories can have parent-child relationships for better organization (self-referencing FK)
- **Transaction Types**: Supports income, expense, and recurring transactions with proper categorization
- **User Data Isolation**: All models filter by `request.user` to ensure complete data separation between users
- **Financial Calculations**: Balance calculations, budget progress, and goal tracking are computed in model properties/methods

### Security Considerations
- User data isolation through model-level filtering
- CSRF protection on all forms
- Session-based authentication with configurable timeouts
- Input validation at both model and form levels

### Performance Patterns
- Database queries optimized with select_related for foreign keys
- Pagination on list views for large datasets
- Calculated fields cached where appropriate
- Static files served efficiently in development

## Coding Standards

Follow PEP 8 strictly with these project-specific conventions:
- Line length: 88 characters (Black compatible)
- Models: PascalCase classes, snake_case fields
- Views: Class-based views preferred, descriptive names
- Templates: Component-based structure in templates/components/
- URLs: Clear, RESTful patterns with app namespaces
- Forms: Custom validation methods with descriptive error messages

### Model Patterns
- Always include created_at/updated_at timestamps
- Use choices for enumerated fields
- Implement __str__ methods for admin and debugging
- Add model-level validation in clean() methods

### View Patterns
- Use LoginRequiredMixin for authenticated views
- Filter querysets by request.user for data isolation
- Handle form validation errors gracefully
- Return appropriate HTTP status codes

### Template Patterns  
- Use custom CSS classes: `.card`, `.btn-primary`, `.form-input` for consistent styling
- Dark theme colors: bg-dark-800, bg-dark-700, text-white, with gradient backgrounds
- Financial color semantics: success (green), danger (red), warning (yellow), primary (blue)
- Responsive breakpoints: sm:, md:, lg:, xl: following mobile-first approach
- Template inheritance from `base.html` with proper static file loading (`{% load static %}`)

## File Structure & Signals Pattern

When implementing Django signals (e.g., for automatic balance updates), follow this pattern:

```
app_name/
├── __init__.py
├── models.py
├── views.py  
├── signals.py          # Put all signals here
├── apps.py             # Import signals in ready() method
└── ...
```

**Example**: For transaction signals that update account balances:
- Create `transactions/signals.py` with post_save/post_delete handlers
- Import signals in `transactions/apps.py` ready() method
- Connect signals to Transaction model changes

## Data Flow

1. **User Authentication**: Django's built-in auth system with Profile extension (OneToOne)
2. **Account Setup**: Users create financial accounts with initial balances
3. **Transaction Processing**: All movements automatically update account balances via signals
4. **Budget Analysis**: Real-time spending tracking against predefined budgets
5. **Goal Monitoring**: Progress calculation based on saved amounts and target dates
6. **Dashboard Aggregation**: Financial overview combining all user data with Chart.js visualizations

The system ensures data consistency through Django ORM relationships, model validation, and signal-based automated updates.