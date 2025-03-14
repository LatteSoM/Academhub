from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import TemplateView, View
from django.views.generic.base import ContextMixin
from django_tables2 import SingleTableView
from django_filters.views import FilterView

from Curriculum.base.navigation import Navigation
from Curriculum.base.sub_table import SubTablesMixin


class NavigationContextMixin(ContextMixin):
    """
    Миксин для добавления навигации в контекст.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navigation'] = Navigation(getattr(self, 'navigation', None)).get()
        return context


class BaseContextMixin(NavigationContextMixin):
    """
    Базовый миксин для добавления контекста.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.get_model_name()
        context['model_urls'] = self.get_model_urls()
        return context

    def get_model_name(self):
        if hasattr(self, 'model'):
            if hasattr(self.model._meta, 'verbose_name'):
                return self.model._meta.verbose_name
            return self.model.__name__
        return ''

    def get_model_urls(self):
        if hasattr(self, 'model'):
            return self.model.get_urls()
        return {}


class ObjectTemplateView(NavigationContextMixin, TemplateView):
    """
    Представление для отображения шаблона.
    """
    pass


class BaseObjectTableView(BaseContextMixin, SingleTableView):
    """
    Базовое представление для отображения таблицы.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_name'] = self.get_table_name()
        return context

    def get_table_name(self):
        return self.table_class.Meta.model._meta.verbose_name_plural


class ObjectTableView(FilterView, BaseObjectTableView):
    """
    Представление для отображения таблицы с фильтрацией.
    """
    pass


class ObjectListView(BaseContextMixin, ListView):
    """
    Представление для отображения списка объектов.
    """
    paginate_by = 10


class ObjectDetailView(BaseContextMixin, SubTablesMixin, DetailView):
    """
    Представление для отображения детальной информации об объекте.
    """

    def get_model_name(self):
        return self.object._meta.verbose_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_tables'] = self.get_tables(self.request, context)
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ObjectUpdateView(BaseContextMixin, UpdateView):
    """
    Представление для обновления объекта.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verbose_name'] = self.get_verbose_name()
        return context

    def get_verbose_name(self):
        return self.object._meta.verbose_name


class ObjectCreateView(BaseContextMixin, CreateView):
    """
    Представление для создания объекта.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verbose_name'] = self.get_verbose_name()
        return context

    def get_verbose_name(self):
        return self.model._meta.verbose_name

    def get_model_name(self):
        return self.model._meta.verbose_name


class ObjectDeleteView(BaseContextMixin, DeleteView):
    """
    Представление для удаления объекта.
    """
    pass


class ObjectDelete(View):
    """
    Удаление обьекта
    """

    def delete(self, request, *args, **kwargs):
        pass