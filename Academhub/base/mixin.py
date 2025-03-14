from django_tables2 import RequestConfig

__all__ = (
    'UrlGenerateMixin',
    'SubTablesMixin',
)

class UrlGenerateMixin:
    '''
        Расширение для моделй django.
        Добавляем автоматческую генерацию наименований url путей CRUD операций у модели
    '''

    url_attrs = [
        'list',
        'delete',
        'create',
        'update',
        'detail',
    ]

    _urls = None

    @classmethod
    def _generate_url(cls):
        cls._urls = {}
        
        for attr in cls.url_attrs:
            prefix_name = 'url_' + attr
            cls._urls[prefix_name] = f'{cls.__name__.lower()}_{attr}'

        return cls._urls
    
    @classmethod
    def _check_urls(cls):
        if not cls._urls:
            cls._generate_url()

    @classmethod
    def get_urls(cls):
        cls._check_urls()
        return cls._urls

    @classmethod
    def set_url(cls, name):
        cls._check_urls()
        cls._urls[name] = name

class SubTablesMixin:
    '''
        Расширение позволяющее выводить на страницу допонительные таблицы.
        
        Поддерживает вывод дочерних таблиц с помошью:
            tables = [
                SubTable (
                    name='Название таблицы',
                    queryset=Model.objects.all(),
                    table=Model,
                    filter_key='pk',
                )
            ]
    '''
    tables = []

    def get_tables(self, request, context):
        context['tables'] = []

        for table in self.tables:
            table.generate_table(self.object)
            RequestConfig(request, paginate={"per_page": self.paginate_by}).configure(table.table)
            context['tables'].append(table)