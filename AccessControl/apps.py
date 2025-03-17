from django.apps import AppConfig


class AccesscontrolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AccessControl'

    def get_navigation(self, user):
        from .navigation import navigation
        return navigation.get(user)