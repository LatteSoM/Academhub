from django import forms

__all__ = (
    'Phone',
    'Snils'
)

# class Phone(forms.TextInput):
#     input_type = 'phone'
#     template_name = 'widgets/phone.html'
#
#     def get_context(self, name, value, attrs):
#         context = super().get_context(name, value, attrs)
#
#         context["widget"]["type"] = self.input_type
#         context["widget"]['attrs']["placeholder"] = '+7 (XXX) XXX-XX-XX'
#
#         return context

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

class Snils(forms.TextInput):
    input_type = 'snils'
    template_name = 'widgets/snils.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context["widget"]["type"] = self.input_type
        context["widget"]['attrs']["placeholder"] = 'XXX-XXX-XXX XX'

        return context