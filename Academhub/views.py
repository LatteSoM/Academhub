from django.urls import reverse_lazy
from .form import CustomAuthenticationForm
from Academhub.base import ObjectTemplateView
from django.contrib.auth.views import LoginView

class HomeView(ObjectTemplateView):
    template_name = "Academhub/index.html"

class CustomLoginView(LoginView):
    template_name = 'Academhub/auth.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')
    form_class = CustomAuthenticationForm