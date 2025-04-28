__all__ = (
    'PermissionMixin',
)

class PermissionMixin:
    '''
        Расширение для объектов имеющие права доступа
    '''
    def get_permissions(self):
        '''
            Получение объекта прав
        '''
        pass
    
    def get_context_data(self, **kwargs):
        '''
            Добавляем в контекст права доступа
        '''
        context = super().get_context_data(**kwargs)
        permissions = self.get_permissions()
        context['permissions'] = permissions.as_context()
        return context