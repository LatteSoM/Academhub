from django.apps import apps
from types import ModuleType

__all__ = (
    'getpattern',
    'getpermission',
)

def _get_model(model: ModuleType | str, app: str = 'Academhub') -> ModuleType:
    if isinstance(model, str):
        try:
            model = apps.get_model(app, model)
        except ValueError:
            raise ValueError(f"Model '{model}' must be in 'app_label.model_name' format (e.g., 'Gradebook.Gradebook').")
        except LookupError:
            raise ValueError(f"Model '{model}' not found.")
    
    return model

def getpattern(model: ModuleType | str, action: str, app: str = 'Academhub') -> str:
    """
    Возвращает pattern_name на основе модели и действия.

    :param model: Модель (как объект модуля или строка с именем модели).
    :param action: Действие (например, "create", "update", "delete", "list").
    :return: Строка с pattern_name.
    """
    # Если model передана как строка, получаем модель по её имени
    model = _get_model(model, app)

    # Получаем словарь URL-паттернов
    urls = model.get_urls()

    # Формируем ключ
    url_key = f'url_{action}'

    # Проверяем, что ключ существует и значение — это строка
    if url_key not in urls:
        raise ValueError(f"URL pattern for action '{action}' not found in model '{model.__name__}'.")
    if not isinstance(urls[url_key], str):
        raise ValueError(f"URL pattern for action '{action}' in model '{model.__name__}' is not a string.")

    return urls[url_key]

def getpermission(model: ModuleType | str, action: str, app: str = 'Academhub') -> str:
    """
    Возвращает permission.codename на основе модели и действия.

    :param model: Модель (как объект модуля или строка с именем модели).
    :param action: Действие (например, "add", "change", "delete", "view").
    :return: Строка с codename.
    """
    # Если model передана как строка, получаем модель по её имени
    model = _get_model(model, app)

    # Получаем имя модели
    model_name = model.__name__.lower()

    # Формируем codenmae
    codename = f'{app}.{action}_{model_name}'
    
    return codename