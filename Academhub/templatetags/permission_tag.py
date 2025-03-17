from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def has_perm(context, permission):
    """
    Проверяет, есть ли у пользователя указанное право.
    :param user: Объект пользователя.
    :param permission: Право в формате 'app_label.codename'.
    :return: True, если право есть, иначе False.
    """
    user = context.get('user')
    if not user or not permission:
        return False

    if user.is_superuser:
        return True

    return user.has_perm(permission)