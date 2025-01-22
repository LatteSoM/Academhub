from django_filters.views import FilterView
from django_tables2 import SingleTableView
from Academhub.base.navigation import Navigation
from django.views.generic.base import ContextMixin
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView

__all__  = [
    'ObjectListView',
    'BaseContextMixin',
    'ObjectDetailView',
    'ObjectUpdateView',
    'ObjectCreateView',
    'ObjectDeleteView',
    'ObjectTemplateView',
]


class BaseContextMixin(ContextMixin):
    """
    Базовый миксин для добавления навигации в контекст всех представлений.
    Наследуется от ContextMixin и добавляет ключ 'navigation' в контекст шаблона.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navigation'] = Navigation().get()
        return context


class ObjectTemplateView(BaseContextMixin, TemplateView):
    '''
    Переопределенный класс TemplateView для поддержки навигации на странице.
    Наследуется от BaseContextMixin и TemplateView.
    Используется для отображения статических страниц с добавлением навигации.
    '''
    pass


class BaseObjectTableView(BaseContextMixin, SingleTableView):
    '''
    Базовый класс для представлений с таблицами.
    Наследуется от BaseContextMixin и SingleTableView (из django-tables2).
    Используется для отображения данных в виде таблиц с поддержкой навигации.
    '''
    def get_table_name(self):
        return self.get_table_class()._meta.model._meta.verbose_name_plural


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_name'] = self.get_table_name()
        return context

class ObjectTableView(FilterView, BaseObjectTableView):
    '''
        Базовый класс для представлений с таблицами.
        Наследуется от BaseContextMixin и SingleTableView (из django-tables2) и FilterView (из django-filter).
        Используется для отображения данных в виде таблиц с фильтрации и поддержкой навигации.
    '''
    pass


class ObjectListView(BaseContextMixin, ListView):
    '''
    Базовый класс для представлений со списками объектов.
    Наследуется от BaseContextMixin и ListView.
    Используется для отображения списка объектов с поддержкой навигации.
    '''
    pass


class ObjectDetailView(BaseContextMixin, DetailView):
    '''
    Базовый класс для представлений с деталями объекта.
    Наследуется от BaseContextMixin и DetailView.
    Используется для отображения деталей одного объекта с поддержкой навигации.
    '''
    pass


class ObjectUpdateView(BaseContextMixin, UpdateView):
    '''
    Базовый класс для представлений с обновлением объекта.
    Наследуется от BaseContextMixin и UpdateView.
    Используется для редактирования существующего объекта с поддержкой навигации.
    '''
    pass


class ObjectCreateView(BaseContextMixin, CreateView):
    '''
    Базовый класс для представлений с созданием объекта.
    Наследуется от BaseContextMixin и CreateView.
    Используется для создания нового объекта с поддержкой навигации.
    '''
    pass


class ObjectDeleteView(BaseContextMixin, DeleteView):
    '''
    Базовый класс для представлений с удалением объекта.
    Наследуется от BaseContextMixin и DeleteView.
    Используется для удаления объекта с поддержкой навигации.
    '''
    pass