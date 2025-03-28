from django.urls import reverse_lazy
from AccessControl.table import GroupTable
from django.views.generic import UpdateView
from AccessControl.mixin import PermissionMixin
from Academhub.models.help.button import Button
from django.contrib.messages.views import SuccessMessageMixin
from Academhub.generic import ObjectTemplateView, ObjectDetailView
from django.contrib.auth.views import LoginView, PasswordChangeView
from .models import CustomUser, SubTable, GroupProxy, PermissionProxy
from AccessControl.form import UserEmailChangeForm, UserPasswordChangeForm
from .forms.form import CustomAuthenticationForm, CustomAuthenticationForm

__all__ = (
    'HomeView',
    'CustomLoginView',
    'UserEmailChangeView',
    'UserPasswordChangeView',
    'UserSettingsDetailView',
)

class HomeView(ObjectTemplateView):
    template_name = "Academhub/index.html"

class CustomLoginView(LoginView):
    template_name = 'Academhub/auth.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')
    form_class = CustomAuthenticationForm

class UserSettingsDetailView(PermissionMixin, ObjectDetailView):
    model = CustomUser
    template_name = 'Academhub/user/personal_account.html'

    fieldset = {
        'Пользовательская информация': [
            'email',
            'full_name',
            'is_staff',
            'is_teacher',
        ],
    }

    buttons = [
        Button (
            name = 'Изменить почту',
            link_name = 'user_email_change',
        ),
        Button (
            name = 'Изменить пароль',
            link_name = 'user_password_change'
        )
    ]

    tables = [
        SubTable (
            name='Группы прав',
            queryset=GroupProxy.objects.all(),
            table=GroupTable,
            filter_key='user',
        )
    ]

    def has_permission(self):
        return True

    def get_object(self, queryset=None):
        return self.request.user

    def get_permissions(self):
        return PermissionProxy.objects.filter(user__id=self.request.user.pk)

class UserEmailChangeView(SuccessMessageMixin, UpdateView):
    """
    Изменение email пользователя
    """
    form_class = UserEmailChangeForm
    success_url = reverse_lazy('home')
    template_name = 'Academhub/user/change_email.html'
    success_message = 'Ваш email был успешно изменён!'

    def get_object(self, queryset=None):
        return self.request.user

class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """
    Изменение пароля пользователя
    """
    form_class = UserPasswordChangeForm
    template_name = 'Academhub/user/change_password.html'
    success_message = 'Ваш пароль был успешно изменён!'