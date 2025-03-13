from django import forms
from Academhub.models import PermissionProxy
from django.template.loader import render_to_string

__all__ = (
    'PermissionSelectWidget',
)

class PermissionSelectWidget(forms.Widget):
    template_name = 'widgets/permissions.html'

    def render(self, name, value, attrs=None, renderer=None):
        permissions = PermissionProxy.objects.select_related('content_type').all()
        
        selected_ids = set(str(v) for v in value or [])
        selected_permissions = []

        for perm in permissions:
            if str(perm.pk) in selected_ids:
                model_name = perm.content_type.model
                codename = perm.codename.split('_')[0]
                selected_permissions.append({
                    'model': model_name,
                    'name': codename,
                    'id': perm.pk,
                })

        context = {
            'name': name,
            'models': permissions.as_context(),
            'selected_permissions': selected_permissions,
            'value': ','.join(selected_ids),
        }

        return render_to_string(self.template_name, context)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, '')
        return value.split(',') if value else []