from django.urls import reverse

# Определяем, какие классы будут доступны при импорте модуля
__all__ = (
    'SubTable',
    'ButtonTable',
)

class ButtonTable:
    '''
    Класс для отображения кнопок таблиц
    permission - права \n
    name - текст кнопки \n
    url - конечный url адрес \n
    link_name - название url адреса \n
    link_params - список параметров url адреса \n
    '''
    
    def __init__(self, name, link_name=None, link_params=None, permission=None):
        # Инициализация объекта кнопки
        self.name = name  # Текст, отображаемый на кнопке
        self.link_name = link_name  # Имя URL-паттерна из Django URL-конфигурации
        self.link_params = link_params or []  # Список параметров для URL, по умолчанию пустой
        self.permission = permission  # Права доступа для кнопки (опционально)
        self.url = None  # Сгенерированный URL, будет заполнен позже

class SubTable:
    '''
    Класс для отображения дополнительных таблиц
    name - название таблицы
    buttons - кнопки таблицы
    table_class - класс таблицы
    queryset - набор данных таблицы
    filter_key - параметр фильтрации
    filter_func - функция фильтрации (более сложная фильтрация)
    '''
    
    def __init__(self, table, queryset, name='', filter_key=None, filter_func=None, buttons=None):
        # Инициализация объекта дополнительной таблицы
        self.name = name  # Название таблицы, по умолчанию пустая строка
        self.buttons = buttons or []  # Список кнопок, по умолчанию пустой список
        self.table_class = table  # Класс таблицы (например, из django-tables2)
        self.queryset = queryset  # Набор данных (QuerySet) для таблицы
        self.filter_key = filter_key  # Ключ для простой фильтрации QuerySet
        self.filter_func = filter_func  # Функция для сложной фильтрации (опционально)
    
    def generate_table(self, object):
        # Метод для генерации таблицы на основе данных и объекта
        self.get_queryset(object)  # Фильтруем данные для таблицы
        self.generate_url_for_buttons(object)  # Генерируем URL для всех кнопок
        self.table = self.table_class(data=self.queryset)  # Создаем экземпляр таблицы с отфильтрованными данными
    
    def generate_url_for_buttons(self, object):
        # Метод для генерации URL для каждой кнопки на основе объекта
        for button in self.buttons:  # Проходим по всем кнопкам таблицы
            if button.link_name:  # Если у кнопки указано имя URL
                if button.link_params:  # Если есть параметры для URL
                    params = {}  # Словарь для хранения параметров URL
                    for param in button.link_params:  # Проходим по каждому параметру
                        # Пробуем получить значение атрибута объекта
                        obj_param = getattr(object, param, None)
                        # Если атрибут не найден, проверяем, является ли он свойством (property)
                        if obj_param is None and hasattr(object.__class__, param):
                            class_attr = getattr(object.__class__, param)
                            if isinstance(class_attr, property):  # Если это свойство
                                obj_param = class_attr.__get__(object, object.__class__)  # Получаем значение свойства
                        params[param] = obj_param  # Добавляем параметр в словарь
                    
                    # Генерируем URL с использованием параметров и сохраняем его в button.url
                    button.url = reverse(button.link_name, kwargs=params)
                else:
                    # Если параметров нет, генерируем URL без аргументов
                    button.url = reverse(button.link_name)

    def get_queryset(self, object):
        # Метод для получения отфильтрованного набора данных
        self.filter_queryset(object)  # Вызываем метод фильтрации

    def filter_queryset(self, object):
        # Метод для фильтрации QuerySet на основе объекта
        if self.filter_func:  # Если указана функция сложной фильтрации
            self.queryset = self.filter_func(object, self.queryset)  # Применяем функцию
        elif self.filter_key:  # Если указан ключ для простой фильтрации
            filter_kwargs = {self.filter_key: object}  # Формируем словарь для фильтрации
            self.queryset = self.queryset.filter(**filter_kwargs)  # Применяем фильтр к QuerySet