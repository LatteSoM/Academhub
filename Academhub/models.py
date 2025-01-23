from django.db import models
from django.shortcuts import reverse

__all__ = {
    'BaseModel'
}

url_attrs = [
    'list',
    'delete',
    'create',
    'update',
    'detail',
]

class AcademHubModel(models.Model):
    _urls = None

    @classmethod
    def _generate_url(cls):
        cls._urls = {}
        
        for attr in url_attrs:
            prefix_name = 'url_' + attr
            cls._urls[prefix_name] = f'{cls.__name__.lower()}_{attr}'

        return cls._urls
    
    @classmethod
    def get_urls(cls):
        if not cls._urls:
            cls._generate_url()

        return cls._urls

    @classmethod
    def set_url(cls, name):
        if not cls._urls:
            cls._generate_url()
            
        cls._urls[name] = name
    
    def get_absolute_url(self):
        url = self.get_urls()['url_detail']
        return reverse(url, kwargs={'pk': self.pk})
    
    class Meta:
        abstract = True