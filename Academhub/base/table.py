from django_tables2 import tables
from django.utils.html import format_html
from django.utils.safestring import mark_safe

class CheckBoxColumn(tables.Column):
    def render(self, value):
        return format_html('<input type="checkbox" name="selected_ids" value="{}" />', value)

    def header(self):
        return mark_safe('<input type="checkbox" name="header" />')

class BaseTable(tables.Table):
    selection = CheckBoxColumn(accessor='pk', orderable=False, verbose_name='')

    def __init__(self, *args, **kwargs):
        if 'selection' not in self._meta.fields:
            self._meta.fields = ('selection',) + self._meta.fields

        super().__init__(*args, **kwargs)