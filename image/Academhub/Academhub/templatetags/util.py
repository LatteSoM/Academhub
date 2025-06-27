from django import template
from django.urls import resolve, Resolver404
from django.urls import reverse, NoReverseMatch

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
   obj_field = getattr(object, field, None)
    
   if not obj_field:
      class_attr = getattr(object.__class__, field, None)
      if isinstance(class_attr, property):
         obj_field = class_attr.__get__(object, object.__class__)
   
   return obj_field

@register.filter
def verbose_name(object, field):
   """
   Возвращает `verbose_name` поля объекта.
   """
   try:
      return object._meta.get_field(field).verbose_name.title()
   except:
      return field

@register.filter
def is_foreign_key(model, field):
   try:
      field = model._meta.get_field(field)
      return field.is_relation
   except:
      return False

@register.filter
def is_many_to_many(model, field):
   try:
      field = model._meta.get_field(field)
      return field.many_to_many
   except:
      return False

@register.filter
def is_one_to_one(model, field):
   try:
      field = model._meta.get_field(field)
      return field.one_to_one
   except:
      return False

@register.simple_tag(takes_context=True)
def paginate_param(context, page_number):
   request = context['request']
   query_dict = request.GET.copy()
   query_dict['page'] = page_number
   return f"{request.path}?{query_dict.urlencode()}"