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


class ImportViewMixin:
    form_import = None
    _form = None

    def generate_form_import(self,*args, **kwargs):
        return self.form_import(**kwargs)

    def save_from_import(self, *args, **kwargs):
        form = self.generate_form_import(**kwargs)
        if form.is_valid():
            form.save()
        return form

    def get(self, request, *args, **kwargs):
        """
            Обработка get запроса
        """
        self._form = self.generate_form_import()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, валидирует и сохраняет form."""
        self._form =  self.save_from_import(request.POST, request.FILES)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_import'] = self._form
        return context


