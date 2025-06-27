from urllib.parse import urlencode

from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def get_query_string_without_page(context):
    request = context['request']
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        del query_dict['page']
    if query_dict:
        return '&' + urlencode(query_dict)
    return ''