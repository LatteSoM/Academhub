from django import forms
from Academhub.forms import PermissionSelectField
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.contenttypes.models import ContentType
from Academhub.models import CustomUser, PermissionProxy, GroupProxy

__all__ = (
    'UserPasswordChangeForm',
    'UserCreateForm',
    'UserUpdateForm',
    'PermissionForm',
    'GroupForm',
)

class UserPasswordChangeForm(SetPasswordForm):
    """
    Форма изменения пароля
    """
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

