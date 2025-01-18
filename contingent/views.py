from django.shortcuts import render

# Create your views here.

def contingent(request):
    return render(request, 'contingent/home.html' )

