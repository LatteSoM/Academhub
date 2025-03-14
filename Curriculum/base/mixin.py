from django.urls import reverse, NoReverseMatch


class UrlGenerateMixin:
    """
    Миксин для генерации URL-адресов.
    """

    @classmethod
    def _generate_url(cls):
        """
        Генерирует URL-адрес.
        """
        if not hasattr(cls, '_url_name'):
            return None

        try:
            if hasattr(cls, 'pk'):
                url = reverse(cls._url_name, kwargs={'pk': cls.pk})
            else:
                url = reverse(cls._url_name)
        except NoReverseMatch:
            url = None

        return url

    @classmethod
    def _check_urls(cls):
        url = cls._generate_url()
        if url is None:
            print(f"Warning: URL name '{cls._url_name}' not found for model {cls.__name__}")

    @classmethod
    def get_urls(cls):
        """
        Возвращает словарь с URL-адресами.
        """
        return {
            'list': cls.set_url('list'),
            'create': cls.set_url('create'),
            'detail': cls.set_url('detail'),
            'update': cls.set_url('update'),
            'delete': cls.set_url('delete'),
        }

    @classmethod
    def set_url(cls, name):
        if hasattr(cls, '_url_name'):
            return cls._url_name.replace('detail', name)
        return None


class SubTablesMixin:
    """
    Миксин для добавления подтаблиц в контекст.
    """

    def get_tables(self, request, context):
        """
        Возвращает список подтаблиц.
        """
        tables = []
        if hasattr(self, 'sub_tables'):
            for table in self.sub_tables:
                tables.append(table.generate_table(self.object))
        return tables