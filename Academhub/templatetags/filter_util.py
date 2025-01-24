from django import template

register = template.Library()

@register.filter(name='get_field_label')
def get_field_label(form, field_name):
    return form.fields[field_name].label

@register.filter(name='get_field_value')
def get_field_value(field, value):
    try:
        if hasattr(field.field, 'queryset'):
            return field.field.queryset.get(pk=value).__str__()
        else:
            return value
    except:
        return value

@register.filter(name='is_list')
def is_list(value):
    print(f'I am {value}')
    return isinstance(value, list)

@register.filter(name='get_list')
def get_list(query_dict, field_name):
    return query_dict.getlist(field_name)

@register.filter(name='trim')
def trim(value):
    return value.strip()