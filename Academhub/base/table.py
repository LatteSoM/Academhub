from django.urls import reverse
from django_tables2 import tables
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

class CheckBoxColumn(tables.Column):
    def render(self, value):
        return format_html('<input type="checkbox" name="selected_ids" value="{}" />', value)

    def header(self):
        return mark_safe('<input type="checkbox" name="header" />')

class ButtonLinkColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        self.url_name = kwargs.pop('url_name', '')
        self.text = kwargs.pop('text', '')
        self.args = kwargs.pop('args', [])

        super().__init__(*args, **kwargs)

    def _set_url_name(self, url_name):
        self.url_name = url_name
        print(self.url_name)

    def render(self, value, record):
        print(f'Url name в методе  render {self.url_name}')
        if self.url_name:
            url = reverse(self.url_name, args=[record.pk])
        else:
            url = '#'

        return render_to_string('inc/table/button.html', {
            "value": value,
            "url": url, 
            "text": self.text
        })

class BaseTable(tables.Table):
    selection = CheckBoxColumn(accessor='pk', orderable=False, verbose_name='')

    edition = ButtonLinkColumn(accessor='pk', text='Изменить', verbose_name='')
    
    view_detail = ButtonLinkColumn(accessor='pk', text='Просмотреть', verbose_name='')

    def __init__(self, *args, **kwargs):
        if 'selection' not in self._meta.fields:
            self._meta.fields = ('selection',) + self._meta.fields
        
        if 'edition' not in self._meta.fields:
            self._meta.fields += ('edition', )
        
        if 'view_detail' not in self._meta.fields:
            self._meta.fields += ('view_detail', )
            
        super().__init__(*args, **kwargs)

        url = self._meta.model.get_urls()

        self.columns['edition'].column._set_url_name(url['url_update'])
        self.columns['view_detail'].column._set_url_name(url['url_detail'])