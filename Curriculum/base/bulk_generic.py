from django.views import View
from django.shortcuts import render, redirect

from Curriculum.base.navigation import NavigationContextMixin


class BulkUpdateView(NavigationContextMixin, View):
    """
    Представление для массового обновления записей.
    """
    formset_class = None  # Класс FormSet, который будет использоваться
    model = None  # Модель, записи которой будут обновляться
    template_name = None  # Шаблон, который будет использоваться для отображения формы
    success_url = None  # URL, на который будет перенаправлен пользователь после успешного обновления

    def get_formset_class(self):
        """
        Возвращает класс FormSet.
        """
        return self.formset_class

    def get_formset(self):
        """
        Возвращает FormSet.
        """
        formset_class = self.get_formset_class()
        return formset_class(**self.get_formset_kwargs())

    def get_formset_kwargs(self):
        """
        Возвращает аргументы для FormSet.
        """
        kwargs = {
            'queryset': self.get_queryset(),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_queryset(self):
        """
        Возвращает QuerySet, который будет использоваться для получения записей.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        return queryset

    def save_form(self, request):
        formset = self.get_formset()
        if formset.is_valid():
            formset.save()
            return True
        return False

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос.
        """
        formset = self.get_formset()
        return render(request, self.template_name, {'formset': formset, **self.get_context_data()})

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос.
        """
        if self.save_form(request):
            return redirect(self.success_url)
        else:
            return self.get(request)