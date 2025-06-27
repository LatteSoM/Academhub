from django.apps import apps
from django.conf import settings

def navigation(request):
    navs = []

    # Проходим по всем активным приложениям
    for app_config in apps.get_app_configs():
        if app_config.label in settings.ACTIVE_APPS:
            try:
                # Пытаемся получить навигацию из AppConfig
                if hasattr(app_config, 'get_navigation'):
                    app_nav = app_config.get_navigation(request.user)
                    navs.extend(app_nav)
            except Exception as e:
                print(f'{app_config}: {e}')

    return {'navigation': navs}