from django import forms

__all__ = (
    'ExcelSheetChoice',
)

class ExcelSheetChoice(forms.ChoiceField):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]['attrs']["placeholder"] = 'Sheet1'
        return context