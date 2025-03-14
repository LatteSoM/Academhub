from django.db import models

__all__ = (
    'UnifiedPermissionQyerySet',
)

class UnifiedPermissionQyerySet(models.QuerySet):

    def as_context(self) -> dict:
        '''
            Объединение действий над моделями в один словарь.
            Возвращает словарь, в котором ключ - название модели, элементы - массив действий.
        '''

        context = {}

        for permission in self.select_related('content_type'):
            model_name = permission.content_type.name
            codename = permission.codename.split('_')[0]
            
            if not context.get(model_name, None):
                context[model_name] = []

            context[model_name].append({
                'id': permission.pk,
                'name': codename
            })
        
        return context

