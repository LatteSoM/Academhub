from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag
def get_button_url(button, obj=None):
    """
    Генерирует URL для кнопки на основе ее параметров и объекта
    """
    if not button.link_name:
        return ''
    
    if not button.link_params:
        return reverse(button.link_name)
    
    params = {}
    for param in button.link_params:
        if obj:
            # Получаем значение параметра из объекта
            value = getattr(obj, param, None)
            # Если параметр не найден как атрибут, проверяем свойство
            if value is None and hasattr(obj.__class__, param):
                class_attr = getattr(obj.__class__, param)
                if isinstance(class_attr, property):
                    value = class_attr.fget(obj)
            params[param] = value
    
    return reverse(button.link_name, kwargs=params) if params else reverse(button.link_name)