from django import forms
from Academhub.models import Permission
from django.template.loader import render_to_string

__all__ = (
    'PermissionSelectWidget',
)

class PermissionSelectWidget(forms.Widget):
    template_name = 'widgets/permissions.html'

    def render(self, name, value, attrs=None, renderer=None):
        permissions = Permission.objects.select_related('content_type').all()

        models = {}

        for permission in permissions:
            model_name = permission.content_type.name
            codename = permission.codename.split('_')[0]
            
            if not models.get(model_name, None):
                models[model_name] = []

            models[model_name].append({
                'id': permission.pk,
                'name': codename
            })
        
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
            'models': models,
            'selected_permissions': selected_permissions,
            'value': ','.join(selected_ids),
        }

        return render_to_string(self.template_name, context)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, '')
        return value.split(',') if value else []