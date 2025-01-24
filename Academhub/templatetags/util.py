from django import template
from django.urls import reverse, NoReverseMatch
from django.urls import resolve, Resolver404

register = template.Library()

@register.filter
def get_type(value):
    return type(value).__name__

@register.filter
def check_url_name_exists(url_name):
    try:
        reverse(url_name)
        return True
    except NoReverseMatch:
        return False

@register.filter
def check_url_exists(url):
    try:
        resolve(url)
        return True
    except Resolver404:
        return False