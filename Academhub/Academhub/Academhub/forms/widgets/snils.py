from django import forms

__all__ = (
    'Snils',
)

class Snils(forms.TextInput):
    input_type = 'snils'
    template_name = 'widgets/snils.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context["widget"]["type"] = self.input_type
        context["widget"]['attrs']["placeholder"] = 'XXX-XXX-XXX XX'

        return context