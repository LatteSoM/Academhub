__all__ = (
    'UrlGenerateMixin',
)

class UrlGenerateMixin:
    '''
        Расширение для моделей Django.
        Добавляем автоматическую генерацию наименований URL-путей CRUD операций у модели
    '''

    url_attrs = [
        'list',
        'delete',
        'add',
        'change',
        'detail',
    ]

    def __init_subclass__(cls, **kwargs):
        """
        Вызывается при создании подкласса (например, CurrentStudent, AcademStudent).
        Создает уникальный словарь _urls для каждого класса.
        """
        super().__init_subclass__(**kwargs)
        # Создаем уникальный словарь _urls для каждого класса
        cls._urls = None  # Инициализируем _urls для нового класса

    @classmethod
    def _generate_url(cls):
        """
        Генерирует словарь URL для текущего класса.
        """
        cls._urls = {}  # Создаем новый словарь для текущего класса
        for attr in cls.url_attrs:
            prefix_name = 'url_' + attr
            cls._urls[prefix_name] = f'{cls.__name__.lower()}_{attr}'
        return cls._urls

    @classmethod
    def _check_urls(cls):
        """
        Проверяет, создан ли словарь _urls, и генерирует его, если он отсутствует.
        """
        if cls._urls is None:
            cls._generate_url()

    @classmethod
    def get_urls(cls):
        """
        Возвращает словарь URL для текущего класса.
        """
        cls._check_urls()
        return cls._urls

    @classmethod
    def set_url(cls, name):
        """
        Устанавливает пользовательский URL в словарь.
        """
        cls._check_urls()
        cls._urls[name] = name