from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType

from Academhub.forms import PermissionSelectField
from django.utils.translation import gettext_lazy as _
from Academhub.models import CustomUser, PermissionProxy, GroupProxy

__all__ = (
    'UserPasswordChangeForm',
    'UserEmailChangeForm',
    'UserCreateForm',
    'UserUpdateForm',
    'PermissionForm',
    'GroupForm',
)

class UserPasswordChangeForm(SetPasswordForm):
    """
    Форма изменения пароля
    """
    new_password1 = forms.CharField(
        label=_("Новый пароль"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    error_messages = {
        'password_mismatch': _("Введённые пароли не совпадают."),
        'password_incorrect': _("Неверный старый пароль. Пожалуйста, попробуйте снова."),
        'password_too_short': _("Пароль слишком короткий. Он должен содержать не менее 8 символов."),
        'password_too_common': _("Этот пароль слишком простой."),
        'password_entirely_numeric': _("Пароль не может состоять только из цифр."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        # Дополнительные проверки пароля (например, сложность)
        if password1:
            if len(password1) < 8:
                raise forms.ValidationError(
                    self.error_messages['password_too_short'],
                    code='password_too_short',
                )
            if password1.isdigit():
                raise forms.ValidationError(
                    self.error_messages['password_entirely_numeric'],
                    code='password_entirely_numeric',
                )
            # Добавьте другие проверки по необходимости
        return password2

class UserEmailChangeForm(forms.ModelForm):
    """
    Форма изменения email
    """
    class Meta:
        model = CustomUser  # Используем вашу кастомную модель
        fields = ['email']

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

class UserCreateForm(forms.ModelForm):
    email = forms.EmailField(
        label='Почта',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'email@email.email'
            }
        ),
    )

    full_name = forms.CharField(
        label='ФИО',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Иванов Иван Иванович'
            }
        ),
    )

    password = forms.Field(
        widget=forms.PasswordInput(),
        label='Пароль'
    )

    groups = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=GroupProxy.objects.all(),
        required=False
    )

    user_permissions = PermissionSelectField(
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password', 'user_permissions', 'groups', 'is_staff', 'is_teacher']

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data['password']

        password = make_password(password)

        cleaned_data['password'] = password

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label='Почта',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'email@email.email'
            }
        ),
    )

    full_name = forms.CharField(
        label='ФИО',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Иванов Иван Иванович'
            }
        ),
    )

    groups = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=GroupProxy.objects.all(),
        required=False
    )

    user_permissions = PermissionSelectField(
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'user_permissions', 'groups', 'is_staff', 'is_teacher']

class GroupForm(forms.ModelForm):
    name = forms.CharField(
        label='Название'
    )

    permissions = PermissionSelectField()

    class Meta:
        model = GroupProxy
        fields = ['name', 'permissions',]

class PermissionForm(forms.ModelForm):
    ACTIONS_CHOICES = (
        ('add', 'add'),
        ('change', 'change'),
        ('view', 'view'),
        ('delete', 'delete')
    )

    name = forms.CharField(
        label='Название'
    )
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(),
        label = 'Модели',
    )

    class Meta:
        model = PermissionProxy
        fields = '__all__'