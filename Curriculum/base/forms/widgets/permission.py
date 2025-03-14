from django import forms
from django.utils.html import format_html


class PermissionsSelectMultiple(forms.SelectMultiple):
    template_name = 'widgets/permissions.html'

    def __init__(self, attrs=None, choices=(), queryset=None):
        self.queryset = queryset
        super().__init__(attrs, choices)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            # Assuming value is a Permission instance
            permission = self.queryset.get(pk=value.value)
            option['attrs']['data-content-type'] = permission.content_type.model
        return option