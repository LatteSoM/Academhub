from django import forms
from django.contrib.auth.models import Permission
from Academhub.base.forms.widgets import PermissionSelectWidget

__all__ = (
    'PermissionSelectField',
)

class PermissionSelectField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Permission.objects.all())
        kwargs.setdefault('widget', PermissionSelectWidget)
        super().__init__(*args, **kwargs)