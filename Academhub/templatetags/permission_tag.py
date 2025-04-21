from django import template
from collections.abc import Iterable

register = template.Library()

@register.simple_tag(takes_context=True)
def has_perm(context, permissions):
    """
    Проверяет, есть ли у пользователя указанное право.
    :param user: Объект пользователя.
    :param permissions: Права в формате 'app_label.codename'.
    :return: True, если право есть, иначе False.
    """
    user = context.get('user')

    if not user:
        return False
    
    if user.is_superuser:
        return True

    if not permissions:
        return False
    
    if isinstance(permissions, Iterable):
        return user.has_perms(permissions)
    else:
        return user.has_perm(permissions)
