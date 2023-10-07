# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter()
def range(min=5):
    return range(min)
