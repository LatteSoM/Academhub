from django.forms import TextInput


class PhoneWidget(TextInput):
    template_name = 'widgets/phone.html'