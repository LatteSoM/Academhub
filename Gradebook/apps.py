from django.apps import AppConfig


class GradebookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Gradebook'

    def get_navigation(self, user):
        from .navigation import navigation
        return navigation.get()
