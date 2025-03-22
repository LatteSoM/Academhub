from django.contrib import messages
from django_tables2 import RequestConfig
from django.views.generic.base import ContextMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

__all__ = (
    'SubTablesMixin',
    'ImportViewMixin',
    'BaseContextMixin',
)

class PermissionBaseMixin(PermissionRequiredMixin):
    '''
        Базовый mixin для реализации прав доступа
    '''
    pass

class BaseContextMixin(ContextMixin):
  """
  Базовый миксин для добавления навигации в контекст всех представлений и прав доступа.
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

class SubTablesMixin:
    '''
        Расширение позволяющее выводить на страницу допонительные таблицы.
        
        Поддерживает вывод дочерних таблиц с помошью:
            tables = [
                SubTable (
                    name='Название таблицы',
                    queryset=Model.objects.all(),
                    table=Model,
                    filter_key='pk',
                    buttons = [
                        ButtonTable (
                            name='Название кнопки',
                            link_name='student_add',
                            permission='add_student'
                        )
                    ]
                )
            ]
    '''
    tables = []

    def get_tables(self, request, context):
        context['tables'] = []

        for table in self.tables:
            table.generate_table(self.object)
            RequestConfig(request, paginate={"per_page": self.paginate_by}).configure(table.table)
            context['tables'].append(table)

class ImportViewMixin:
    form_import = None
    _form = None

    def generate_form_import(self, *args, **kwargs):
        return self.form_import(*args, **kwargs)

    def save_from_import(self, *args, **kwargs):
        form = self.generate_form_import(*args, **kwargs)
        if form.is_valid():
            form.save()
        return form

    def get(self, request, *args, **kwargs):
        """
            Обработка get запроса
        """
        self._form = self.generate_form_import()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, валидирует и сохраняет form."""

        self._form =  self.save_from_import(request.POST, request.FILES)

        if self._form.is_valid():
            print("=== form.is_valid() is True ===") # Debug print
            messages.success(
                request,
                "Успешный импорт"
            )
            
            self._form = self.generate_form_import()
        else:
            error_message = "Импорт не удался: \n"
            for field, errors in self._form.errors.items():
                error_message += f"{', '.join(errors)}\n"

            messages.error(
                request,
                error_message
            )
        
        return super().get(request, *args, **kwargs)
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_import'] = self._form
        return context