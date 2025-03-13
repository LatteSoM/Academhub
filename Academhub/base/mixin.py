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
        
        for attr in self.url_attrs:
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
                    table_class=ModelTable,
                    buttons = [
                        ButtonTable (
                            name = 'Название кнопки',
                            link = 'home'
                        )
                    ]
                )
            ]

            tables = {
                'Название таблицы': {
                    'queryset': Model.objects.all(),
                    'table_class': ModelTable,
                    'buttons': [
                        'Название кнопки': {
                            'link': 'home'
                        }
                    ]
                }
            }
    '''
    tables = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tables'] = self.tables
        return context

    def get_tables(self, request):
        for table in self.tables:
            RequestConfig(request, paginate={"per_page": self.paginate_by }).configure(table)