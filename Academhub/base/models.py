from django.db import models
from .mixin import UrlGenerateMixin
from django.shortcuts import reverse

__all__ = (
    'AcademHubModel',
)

class AcademHubModel(UrlGenerateMixin, models.Model):
    def get_absolute_url(self):
        url = self.get_urls()['url_detail']
        return reverse(url, kwargs={'pk': self.pk})
    
    class Meta:
        abstract = True