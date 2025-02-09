from django import template
from django.urls import reverse, NoReverseMatch
from django.urls import resolve, Resolver404

register = template.Library()

@register.filter
def get_type(value):
   """
   Возвращает имя типа значения.
   """
   return type(value).__name__

@register.filter
def check_url_name_exists(url_name):
   """
   Проверяет, существует ли URL с указанным именем.
   """
   try:
       reverse(url_name)
       return True
   except NoReverseMatch:
       return False

@register.filter
def check_url_exists(url):
   """
   Проверяет, существует ли URL.
   """
   try:
       resolve(url)
       return True
   except Resolver404:
       return False

@register.filter
def exclude_field(form, field):
   """
   Исключает поле с указанным именем.
   """
   return [field for field in form if field.name != field]

@register.filter
def get_url(model, url_name):
   """
   Возвращает URL с указанным именем для модели.
   """
   return model.get_urls()[url_name]

@register.filter
def get_item(dictionary, key):
   """
   Возвращает значение из словаря по ключу.
   """
   return dictionary[key]

@register.filter
def attr(object, field):
   """
   Возвращает атрибут объекта по имени поля.
   """
   return getattr(object, field)

@register.filter
def verbose_name(object, field):
   """
   Возвращает `verbose_name` поля объекта.
   """
   return object._meta.get_field(field).verbose_name.title()

@register.filter
def is_foreign_key(model, field):
    field = model._meta.get_field(field)
    return field.is_relation

@register.filter
def is_many_to_many(model, field):
    field = model._meta.get_field(field)
    return field.many_to_many

@register.filter
def is_one_to_one(model, field):
    field = model._meta.get_field(field)
    return field.one_to_one