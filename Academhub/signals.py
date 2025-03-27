# myproject/signals.py
import importlib
from django.apps import apps
from .settings import ACTIVE_APPS
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

def create_custom_permissions(sender, **kwargs):
    # Получаем все установленные приложения
    all_apps = apps.get_app_configs()

    for app_config in all_apps:
        app_label = app_config.label
        # Пропускаем системные приложения Django, если нужно
        if app_label in ACTIVE_APPS:
            permissions = []
            # Проверяем, есть ли в приложении файл permissions.py с PERMISSIONS
            try:
                permissions_module = importlib.import_module(f"{app_label}.permissions")
                permissions = getattr(permissions_module, 'PERMISSIONS', [])
            except (ImportError, AttributeError) as e:
                print(e)

            # Создаём фиктивный ContentType для приложения
            content_type, created = ContentType.objects.get_or_create(
                app_label=app_label,
                model=app_label,  # Фиктивная модель
            )

            # Создаём права из словаря PERMISSIONS
            for perm in permissions:
                Permission.objects.get_or_create(
                    codename=perm['codename'],
                    name=perm['name'],
                    content_type=content_type,
                )

def setup_signals():
    # Отключаем все стандартные обработчики post_migrate, которые создают права
    post_migrate.receivers = []

    # Подключаем наш обработчик для каждого приложения
    for app_config in apps.get_app_configs():
        post_migrate.connect(create_custom_permissions, sender=app_config)