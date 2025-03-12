from django import forms
from Academhub.base.forms import PermissionSelectField
from django.contrib.contenttypes.models import ContentType
from Academhub.models import CustomUser, PermissionProxy, GroupProxy

class UserForm(forms.ModelForm):
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
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password', 'user_permissions', 'groups', 'is_staff', 'is_teacher']

class GroupForm(forms.ModelForm):
    name = forms.CharField(
        label='Название'
    )

    permissions = PermissionSelectField()

    users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        label='Пользователи',
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = GroupProxy
        fields = '__all__'

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
