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
        Класс для отображения дополнительных таблиц
        name - название таблицы
        buttons - tнопки таблицы
        queryset - набор данных таблицы
        table_class - класс таблицы
    '''
    name=''
    buttons = []
    queryset = None
    table = None

    def __init__(self):
        self.table = self.table(data=self.queryset)