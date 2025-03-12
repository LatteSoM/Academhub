from django.shortcuts import render
from django.views.generic import View
from django.forms import modelformset_factory
from .generic import NavigationContextMixin

__all__ = (
    'BulkUpdateView',
)

class BulkUpdateView(NavigationContextMixin, View):
    extra = 0
    model = None
    form_class = None
    success_url = None
    template_name = ''

    def get_formset_class(self):
        return modelformset_factory(
            extra=self.extra,
            model=self.model,
            form=self.form_class,
        )
    
    def get_formset(self):
        return self.get_formset_class()(queryset=self.get_queryset())

    def get_queryset(self):
        return self.model.objects.all()
    
    def save_form(self, request):
        FormSet = self.get_formset_class()
        formset = FormSet(request.POST, request.FILES)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.save()

        return formset
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(formset=self.get_formset())
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, валидирует и сохраняет formset."""
        return render(request, 
            self.template_name, 
            self.get_context_data(formset=self.save_form(request))
        )
