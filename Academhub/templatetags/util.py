from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.filter
def get_type(value):
    return type(value).__name__

@register.filter
def check_url_exists(url_name):
    try:
        reverse(url_name)
        return True
    except NoReverseMatch:
        return False