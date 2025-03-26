from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    """Возвращает поле формы по его имени"""
    try:
        return form[field_name]
    except KeyError:
        return None
