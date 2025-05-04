from collections.abc import Iterable

from django import template

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
    print('Навигация')
    print(f'user: {user}')
    print(permissions)
    
    if isinstance(permissions, Iterable):
        result = user.has_perms(permissions)
    else:
        result = user.has_perm(permissions)
    print(result)
    

    return result
