from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    """Возвращает поле формы по его имени"""
    try:
        return form[field_name]
    except KeyError:
        return None

@register.filter
def get_item(value, key):
    """Универсальный фильтр для работы со словарями и объектами"""
    try:
        if isinstance(value, dict):
            return value.get(key, '-')
        elif hasattr(value, 'get'):
            return value.get(key, '-')
        elif hasattr(value, str(key)):
            return getattr(value, str(key), '-')
        return '-'
    except Exception:
        return '-'
