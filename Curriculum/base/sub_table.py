class ButtonTable:
    def __init__(self, text, url, class_name='btn btn-primary'):
        self.text = text
        self.url = url
        self.class_name = class_name


class SubTable:
    """
    Класс для создания подтаблицы.
    """

    def __init__(self, table, queryset, name='', filter_key=None, filter_func=None):
        self.table = table
        self.queryset = queryset
        self.name = name
        self.filter_key = filter_key
        self.filter_func = filter_func

    def generate_table(self, object):
        """
        Генерирует таблицу.
        """
        queryset = self.get_queryset(object)
        if self.filter_key and self.filter_func:
            queryset = self.filter_queryset(queryset)
        return self.table(queryset)

    def get_queryset(self, object):
        """
        Возвращает QuerySet.
        """
        if callable(self.queryset):
            return self.queryset(object)
        return self.queryset.all()

    def filter_queryset(self, object):
        """
        Фильтрует QuerySet.
        """
        kwargs = {self.filter_key: object}
        return self.filter_func(**kwargs)