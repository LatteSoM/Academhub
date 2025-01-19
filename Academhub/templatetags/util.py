from django import template

register = template.Library()

@register.filter
def get_type(value):
    print(type(value).__name__)
    return type(value).__name__
