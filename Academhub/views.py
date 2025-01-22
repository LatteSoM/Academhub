from django.shortcuts import render
from Academhub.base import ObjectTemplateView

class HomeView(ObjectTemplateView):
    template_name = "Academhub/index.html"

def auth(request):
    return render(request, 'Academhub/auth.html')