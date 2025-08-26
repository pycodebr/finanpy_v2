from django import template
from django.utils.safestring import mark_safe
from decimal import Decimal

register = template.Library()


@register.filter
def currency_format(value, currency='BRL'):
    """
    Format a decimal value as Brazilian currency.
    Usage: {{ value|currency_format:"BRL" }}
    """
    if value is None:
        return "R$ 0,00"
    
    try:
        # Convert to float for formatting
        val = float(value)
        
        # Format number in Brazilian style: 1.234,56
        formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'BRL': 'R$',
            'GBP': '£',
            'CAD': 'C$',
        }
        
        symbol = currency_symbols.get(currency, currency)
        return f"{symbol} {formatted}"
        
    except (ValueError, TypeError):
        return "R$ 0,00"


@register.filter  
def date_format_br(value):
    """
    Format a date in Brazilian format (dd/mm/yyyy).
    Usage: {{ date_field|date_format_br }}
    """
    if value is None:
        return ""
    
    try:
        return value.strftime("%d/%m/%Y")
    except (AttributeError, TypeError):
        return str(value)


@register.filter
def datetime_format_br(value):
    """
    Format a datetime in Brazilian format (dd/mm/yyyy HH:mm).
    Usage: {{ datetime_field|datetime_format_br }}
    """
    if value is None:
        return ""
    
    try:
        return value.strftime("%d/%m/%Y %H:%M")
    except (AttributeError, TypeError):
        return str(value)