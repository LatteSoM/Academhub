from .mixin import SubTablesMixin
from .navigation import Navigation
from django.http import JsonResponse
from django_tables2 import SingleTableView
from django_filters.views import FilterView
from django.utils.translation import gettext as _
from django.views.generic.base import ContextMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView, View

__all__  = [
  'ObjectListView',
  'BaseContextMixin',
  'ObjectDetailView',
  'ObjectUpdateView',
  'ObjectCreateView',
  'ObjectDeleteView',
  'ObjectTemplateView',
]

class NavigationContextMixin(ContextMixin):
  """
      Базовый миксин для добавления навигации в контекст всех представлений.
      Наследуется от ContextMixin и добавляет ключ 'navigation' в контекст шаблона.
  """

  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['navigation'] = Navigation().get()
      return context

class BaseContextMixin(NavigationContextMixin):
  """
  Базовый миксин для добавления навигации в контекст всех представлений.
  Наследуется от ContextMixin и добавляет ключ 'navigation' в контекст шаблона.
  """
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['model_name'] = self.get_model_name()

      return context | self.get_model_urls()

  def get_model_name(self):
        model_class = self.queryset.model
        return model_class._meta.model_name

  def get_model_urls(self):
      if getattr(self, 'model'):
          return self.model.get_urls()
      else:
          return self.queryset.model.get_urls()


class ObjectTemplateView(NavigationContextMixin, TemplateView):
  '''
  Переопределенный класс TemplateView для поддержки навигации на странице.
  Наследуется от NavigationContextMixin и TemplateView.
  Используется для отображения статических страниц с добавлением навигации.
  '''




class BaseObjectTableView(BaseContextMixin, SingleTableView):
    '''
    Базовый класс для представлений с таблицами.
    Наследуется от BaseContextMixin и SingleTableView (из django-tables2).
    Используется для отображения данных в виде таблиц с поддержкой навигации.
    '''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_name'] = self.get_table_name()
        return context

    def get_table_name(self):
        return self.get_table_class()._meta.model._meta.verbose_name_plural

class ObjectTableView(FilterView, BaseObjectTableView):
    '''
      Базовый класс для представлений с таблицами.
      Наследуется от BaseContextMixin и SingleTableView (из django-tables2) и FilterView (из django-filter).
      Используется для отображения данных в виде таблиц с фильтрации и поддержкой навигации.
    '''
    template_name = 'base_view.html'
    paginate_by = 10


class ObjectListView(BaseContextMixin, ListView):
    '''
    Базовый класс для представлений со списками объектов.
    Наследуется от BaseContextMixin и ListView.
    Используется для отображения списка объектов с поддержкой навигации.
    '''
    pass


class ObjectDetailView(BaseContextMixin, SubTablesMixin, DetailView):
    '''
        Базовый класс для представлений с деталями объекта.
        Наследуется от BaseContextMixin и DetailView.
        Используется для отображения деталей одного объекта с поддержкой навигации.

        Поддерживаем вывод и группировки полей с помощью:
            fieldset = {
                'Основная информация': - название группировки полей
                    ['field1', 'field2'], - поля
                'Дополнительная информация': 
                    ['field3', 'field4'],
            }
        
        Поддерживает вывод дополнительных таблиц благодаря SubTablesMixin.
    '''
    paginate_by  = 10
    template_name = 'base_detail.html'

    fieldset = {}

    tables = []

    def get_model_name(self):
        return self.model._meta.model_name
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fieldset'] = self.fieldset
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        self.get_tables(request, context)

        return self.render_to_response(context)


class ObjectUpdateView(BaseContextMixin, UpdateView):
    '''
    Базовый класс для представлений с обновлением объекта.
    Наследуется от BaseContextMixin и UpdateView.
    Используется для редактирования существующего объекта с поддержкой навигации.
    '''
    template_name = 'base_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mobel_verbosename'] = self.get_verbose_name()
        return context

    def get_verbose_name(self):
        model_class = self.queryset.model
        return model_class._meta.verbose_name

class ObjectCreateView(BaseContextMixin, CreateView):
    '''
    Базовый класс для представлений с созданием объекта.
    Наследуется от BaseContextMixin и CreateView.
    Используется для создания нового объекта с поддержкой навигации.
    '''
    template_name = 'base_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mobel_verbosename'] = self.get_verbose_name()
        return context

    def get_verbose_name(self):
        return self.model._meta.verbose_name

    def get_model_name(self):
        return self.model._meta.model_name

class ObjectDeleteView(BaseContextMixin, DeleteView):
    '''
        Базовый класс для представлений с удалением объекта.
        Наследуется от BaseContextMixin.
        Используется для удаления объекта с поддержкой навигации и возможностью отмены.
    '''

class ObjectDelete(View):
    '''
    Базовый класс для для удалением объекта.
    Наследуется от View.
    '''
    queryset = None


    def delete(self, request, *args, **kwargs):
        if not self.queryset:
            return JsonResponse({'error': 'Model is not specified'}, status=500)
        
        pk = kwargs.get('pk')

        result = {}
        status = 200

        try:
            obj = self.queryset.get(pk=pk)
            obj.delete()
            result[pk] = None 

        except ObjectDoesNotExist:
            status = 400
            result[pk] = 'Object not found'

        except Exception:
            status = 500
            result[pk] = 'Server error. Try later'
        
        return JsonResponse(result, status)
