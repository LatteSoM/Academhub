from .generic import NavigationContextMixin
from django.forms import modelformset_factory
from django.views.generic import UpdateView

__all__ = (
    'BulkUpdateView',
)

class BulkUpdateView(NavigationContextMixin, UpdateView):
    """
    View for updating multiple objects using a formset.
    """
    model = None
    queryset = None
    form_class = None

    def get_formset_class(self):
        """
        Возвращает класс formset. Если formset_class не указан, создает его на основе model и form_class.
        """
        if self.formset_class:
            return self.formset_class
        return modelformset_factory(
            self.model,
            form=self.form_class,
            extra=0
        )

    def get_queryset(self):
        """
        Возвращает QuerySet для объектов, которые будут редактироваться.
        """
        if self.queryset is not None:
            return self.queryset
        return self.model.objects.all()

    def get_formset(self):
        """
        Возвращает инициализированный formset.
        """
        FormSet = self.get_formset_class()
        return FormSet(queryset=self.get_queryset())

    def get_context_data(self, **kwargs):
        """
        Добавляет formset в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        context['formset'] = self.get_formset()
        return context

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос и сохраняет изменения в formset.
        """
        FormSet = self.get_formset_class()
        formset = FormSet(request.POST)

        # Если форма невалидна, возвращаем форму с ошибками
        return self.render_to_response(self.get_context_data(formset=formset))