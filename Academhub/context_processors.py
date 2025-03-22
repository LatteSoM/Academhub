import importlib
from django.conf import settings
from Academhub.models import Navigation

def navigation(request):

    for app in settings.ACTIVE_APPS:
        importlib.import_module(f"{app}.navigation")

    return {'navigation': Navigation().get()}