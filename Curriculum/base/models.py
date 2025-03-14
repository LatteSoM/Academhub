from django.db import models
from django.urls import reverse

from Curriculum.base.mixin import UrlGenerateMixin


class AcademHubModel(UrlGenerateMixin, models.Model):
    """
    Абстрактная модель для приложения Academhub.
    """

    def get_absolute_url(self):
        """
        Возвращает URL-адрес для просмотра объекта.
        """
        if hasattr(self, '_url_name'):
            return reverse(self._url_name, kwargs={'pk': self.pk})
        return None

    class Meta:
        abstract = True