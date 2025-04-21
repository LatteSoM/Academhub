from django import forms
from django.contrib.auth.models import Permission
from django.template.loader import render_to_string

__all__ = (
    'ExcelCell',
)

class ExcelCell(forms.TextInput):
    input_type = 'excel_cell'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]['attrs']["placeholder"] = 'A2:B3'
        return context