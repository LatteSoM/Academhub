from ..utils import getpermission
from django.contrib import messages
from django_tables2 import RequestConfig
from django.views.generic.base import ContextMixin
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin

__all__ = (
    'ButtonsMixin',
    'SubTablesMixin',
    'ImportViewMixin',
    'BaseContextMixin',
    'PermissionBaseMixin',
)

class PermissionBaseMixin(PermissionRequiredMixin):
    '''
        Базовый mixin для ограничения доступа к странциам на основе прав доступа
    '''

    def _get_class_object(self):
        try:
            if self.model is not None:
                return self.model
        except AttributeError:
            pass

        try:
            if self.queryset is not None:
                return self.queryset.model
        except AttributeError:
            pass

        raise ImproperlyConfigured(
            f"{self.__class__.__name__} is missing both 'model' and 'queryset' attributes. "
            f"Define either {self.__class__.__name__}.model or {self.__class__.__name__}.queryset."
        )

    def get_permission_required(self):
        if self.permission_required is None:
            return None

        model = self._get_class_object()

        perm = getpermission(model, self.permission_required)

        return [perm, ]
    
    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        perms = self.get_permission_required()
        if not perms:
            return True
        return self.request.user.has_perms(perms)

class ButtonsMixin:
    """
        Расширение позволяющие выводить на страницу кнопки с возможностью их  кастомизирования

        Поддерживается вывод кнопок с помощью:

        buttons = [
            Button (
                name = 'Название кнопки'
                url = 'Url адресс'
                permission_required = 'model_add'
                id='unique_name'
            )
        ]
    """

    buttons = []

    def get_buttons_object(self):

        if hasattr(self, 'object'):
            return self.object
        
        try:
            return self.model
        except AttributeError:
            pass
        
        try:
            return self.queryset.model
        except AttributeError:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        buttons = []

        for button in self.buttons:
            if button.is_accessible(self.request.user):
                buttons.append(button)

        context['buttons'] = buttons

        return context

class BaseContextMixin(PermissionBaseMixin, LoginRequiredMixin, ButtonsMixin, ContextMixin):
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