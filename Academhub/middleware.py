from django.http import HttpResponseRedirect
from django.urls import reverse

class AuthMiddleware:
    '''
        Middleware для проверки авторизации пользователя.
        Если пользователь не авторизован и пытается получить доступ к защищенным страницам, 
        он будет перенаправлен на страницу авторизации.
    '''
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user = request.user

        if not user.is_authenticated and request.path != reverse('login'):
            return HttpResponseRedirect(reverse('login')) 

        return self.get_response(request)