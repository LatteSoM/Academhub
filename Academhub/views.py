from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.views.generic import UpdateView

from AccessControl.form import UserPasswordChangeForm, UserEmailChangeForm
from AccessControl.table import GroupTable
from AccessControl.views import PermissionMixin
from .forms.form import CustomAuthenticationForm
from Academhub.generic.generic import ObjectTemplateView, ObjectDetailView, ObjectUpdateView

__all__ = (
    'HomeView',
    'CustomLoginView'
)

from .models import CustomUser, SubTable, GroupProxy, PermissionProxy


class HomeView(ObjectTemplateView):
    template_name = "Academhub/index.html"

class CustomLoginView(LoginView):
    template_name = 'Academhub/auth.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')
    form_class = CustomAuthenticationForm


class SettingsView(ObjectTemplateView):
    template_name = 'Academhub/settings.html'


class UserSettingsDetailView(PermissionMixin, ObjectDetailView):
    model = CustomUser
    template_name = 'Academhub/settings.html'

    fieldset = {
        'Пользовательская информация': [
            'email',
            'full_name',
            'is_staff',
            'is_teacher',
            'is_active',
            # 'last_login'
        ],
    }

    tables = [
        SubTable (
            name='Группы прав',
            queryset=GroupProxy.objects.all(),
            table=GroupTable,
            filter_key='user',
        )
    ]

    def get_permissions(self):
        return PermissionProxy.objects.filter(user__id=self.object.pk)

class UserEmailChangeView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Изменение email пользователя
    """
    form_class = UserEmailChangeForm
    template_name = 'AccessControl/update/change_email.html'
    success_message = 'Ваш email был успешно изменён!'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user