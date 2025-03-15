__all__ = (
    'SubTable',
)

class ButtonTable:
    '''
        Класс для отображения кнопок таблиц
    '''
    name=''
    link=''

class SubTable:
    '''
        Класс для отображения дополнительных таблиц \n
        name - название таблицы \n
        buttons - tнопки таблицы \n
        table_class - класс таблицы \n
        queryset - набор данных таблицы \n
        filter_key - параметр фильтрации
        filter_func - функция фильтрации (более сложная фильтрация)
    '''
    
    def __init__(self, table, queryset, name='', filter_key=None, filter_func=None):
        self.name = name
        self.table_class = table
        self.queryset = queryset
        self.filter_key = filter_key
        self.filter_func = filter_func
    
    def generate_table(self, object):
        self.get_queryset(object)
        self.table = self.table_class(data=self.queryset)

    def get_queryset(self, object):
        self.filter_queryset(object)

    def filter_queryset(self, object):
        if self.filter_func:
            self.queryset = self.filter_func(object, self.queryset)
        elif self.filter_key:
            filter_kwargs = {self.filter_key: object}
            self.queryset = self.queryset.filter(**filter_kwargs)