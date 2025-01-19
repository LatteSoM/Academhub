from django.shortcuts import render


def auth(request):
    return render(request, 'Academhub/auth.html')

def home(request):
    return render(request, 'Academhub/index.html')