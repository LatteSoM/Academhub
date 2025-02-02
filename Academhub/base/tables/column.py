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

        try:
            url = reverse(self.url_name, args=[record.pk])
        except:
            url = '#'


        return render_to_string('inc/table/button.html', {
            "value": value,
            "url": url, 
            "text": self.text
        })

class EmailColumn(tables.Column):
    def render(self, value):
        return format_html('{}', value)