# from django.urls import reverse

__all__ = (
    'SubTable',
)

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
        self.table = self.table_class(data=self.queryset)  # Создаем экземпляр таблицы с отфильтрованными данными

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