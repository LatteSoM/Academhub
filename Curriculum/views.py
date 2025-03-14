from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views.generic import TemplateView

from Curriculum.base.generic import ObjectTemplateView


# Create your views here.
class HomeView(ObjectTemplateView):
    """
    Главная страница
    """
    template_name = 'Academhub/index.html'


class CustomLoginView(LoginView):
    """
    Авторизация
    """
    template_name = 'Academhub/auth.html'
