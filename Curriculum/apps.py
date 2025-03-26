from django.apps import AppConfig


class CurriculumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Curriculum'

    def get_navigation(self, user):
        from .navigation import navigation
        return navigation.get()
