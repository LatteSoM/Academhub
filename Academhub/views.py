from django.shortcuts import render
from django.views.generic import TemplateView
from .base_navigation import Navigation


class BaseView(TemplateView):
    template_name = "Academhub/index.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['navigation'] = Navigation().get()
        return data


def auth(request):
    return render(request, 'Academhub/auth.html')


def home(request):
    return render(request, 'Academhub/index.html')