from django import forms
from django.contrib.auth.models import Permission
from django.template.loader import render_to_string

__all__ = (
    'Phone',
)

class Phone(forms.TextInput):
    input_type = 'tel'  # Используем type="tel" для лучшей поддержки на мобильных

    template_name = 'widgets/phone.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["type"] = self.input_type
        context["widget"]['attrs']["placeholder"] = '+7 (___) ___-__-__'
        context["widget"]['attrs']["maxlength"] = "18"  # Ограничиваем ввод
        context["widget"]['attrs']["data-mask"] = "phone"  # Используем data-атрибут для JS
        return context