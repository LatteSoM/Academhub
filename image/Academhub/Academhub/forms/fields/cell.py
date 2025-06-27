from django import forms

__all__ = (
    'ExcelCell',
)

class ExcelCell(forms.TextInput):
    input_type = 'excel_cell'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]['attrs']["placeholder"] = 'A2:B3'
        return context