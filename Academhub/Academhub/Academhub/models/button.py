from django.urls import reverse

__all__ = (
    'Button',
)

class Button:
    '''
    Класс для отображения кнопок
    permission - права \n
    name - текст кнопки \n
    link_name - название url адреса \n
    link_params - список параметров url адреса \n
    '''
    
    def __init__(self, name, id=None, link_name=None, link_params=None, permission=None):
        # Инициализация объекта кнопки
        self.id = id
        self.name = name  # Текст, отображаемый на кнопке
        self.link_name = link_name  # Имя URL-паттерна из Django URL-конфигурации
        self.link_params = link_params or []  # Список параметров для URL, по умолчанию пустой
        self.permission = permission  # Права доступа для кнопки (опционально)
    
    def is_accessible(self, user):
        '''
            Проверка проходил ли кнопка по правам
        '''
        if self.permission:
            if user.is_superuser:
                return True
            else:
                return user.has_perm(self.permission)
        else:
            return True