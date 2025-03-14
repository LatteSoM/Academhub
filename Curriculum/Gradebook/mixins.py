from django.shortcuts import redirect
from django.urls import reverse_lazy

from Curriculum.models import Gradebook


class GradeBookMixin:
    """
    Миксин для ведомости
    """

    def get_properties(self, request):
        gradebook_id = self.kwargs.get('pk')
        if gradebook_id:
            gradebook = Gradebook.objects.get(pk=gradebook_id)
            return {
                'gradebook': gradebook,
                'group': gradebook.group,
                'teacher': gradebook.teacher,
                'curriculum_item': gradebook.curriculum_item,
            }
        return {}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(self.get_properties(self.request))
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        properties = self.get_properties(request)
        if properties:
            if properties['teacher'] != request.user:
                return redirect('home')
        return super().dispatch(request, *args, **kwargs)