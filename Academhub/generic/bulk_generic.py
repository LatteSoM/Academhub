from django.views.generic import View
from django.forms import modelformset_factory
from django.shortcuts import render, redirect


__all__ = (
    'BulkUpdateView',
)

from django.views.generic.base import ContextMixin


class BulkUpdateView(ContextMixin, View):
    """
        Класс для обработки можественного обновления объектов
    """
    _is_save = False # флаг сохранения формы
    model = None # класс который будет обновляться
    form_class = None # класс формы
    success_url = '' # url на который будет происходить переадресация в случае успешного сохранения формы
    template_name = '' # Путь до html страницы 

    def get_formset_class(self):
        """
            Получение класса формы
        """
        return modelformset_factory(
            extra=0,
            model=self.model,
            form=self.form_class,
        )
    
    def get_formset(self):
        """
            Получение формы
        """
        return self.get_formset_class()(queryset=self.get_queryset())

    def get_queryset(self):
        """
            Получение queryset
        """
        return self.model.objects.all()
    
    def save_form(self, request):
        """
            Сохранение формы
        """
        FormSet = self.get_formset_class()
        formset = FormSet(request.POST, request.FILES)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.save()
                is_save = True

        return formset
    
    def get(self, request, *args, **kwargs):
        """
            Обработка get запроса
        """
        context = self.get_context_data(formset=self.get_formset())
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, валидирует и сохраняет formset."""
        formset = self.save_form(request)

        if self._is_save:

            if self.success_url != '':
                return redirect(self.success_url)
            
            return redirect(self.model.get_urls['list'])
        
        context =  self.get_context_data(formset)

        return render(request, 
            self.template_name, 
            context
        )
        
