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
        self.button_url = None  # Сгенерированный URL, будет заполнен позже
    
    def generate_url(self, object):
        if not self.button_url:
            if self.link_name:
                if self.link_params:
                    params = {}
                    for param in self.link_params:
                        # Получаем значение параметра из объекта
                        obj_param = getattr(object, param, None)

                        # Если параметр не найден как атрибут, проверяем, является ли он свойством
                        if obj_param is None and hasattr(object.__class__, param):
                            class_attr = getattr(object.__class__, param)
                            if isinstance(class_attr, property):
                                # Извлекаем значение свойства
                                obj_param = class_attr.fget(object)
                        params[param] = obj_param

                    # Генерируем URL с конкретными значениями
                    self.button_url = reverse(self.link_name, kwargs=params)
                else:
                    self.button_url = reverse(self.link_name)
    
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
