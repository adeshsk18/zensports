from django import template
from datetime import timedelta

register = template.Library()

@register.filter(name='add_days')
def add_days(value, days):
    """Add a number of days to a date."""
    if value:
        try:
            return value + timedelta(days=int(days))
        except (ValueError, TypeError):
            return value
    return value 