from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .forms.form import CustomAuthenticationForm
from Academhub.generic.generic import ObjectTemplateView

__all__ = (
    'HomeView',
    'CustomLoginView'
)

class HomeView(ObjectTemplateView):
    template_name = "Academhub/index.html"

class CustomLoginView(LoginView):
    template_name = 'Academhub/auth.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')
    form_class = CustomAuthenticationForm