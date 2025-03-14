from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if dictionary:
        return dictionary.get(key)
    return None


@register.filter
def get_attr(obj, key):
    return getattr(obj, key)