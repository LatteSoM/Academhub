from django.forms import TextInput


class SnilsWidget(TextInput):
    template_name = 'widgets/snils.html'