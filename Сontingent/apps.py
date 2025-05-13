from django.apps import AppConfig


class ContingentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Сontingent'

    def get_navigation(self, user):
        from .navigation import navigation
        return navigation.get()