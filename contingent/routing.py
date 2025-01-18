from django.urls import path
import contingent.views as v
from .views import *
from Academhub import settings
from django.conf.urls.static import static as djstat

urlpatterns = [
    path('start/', v.contingent),

] + djstat(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
