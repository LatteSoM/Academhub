from django import forms
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

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password', 'user_permissions', 'groups', 'is_staff', 'is_teacher']

class GroupForm(forms.ModelForm):
    name = forms.CharField(
        label='Название'
    )
    permissions = forms.ModelMultipleChoiceField(
        queryset=PermissionProxy.objects.all(),
        label='Права'
    )
    users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        label='Пользователи'
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
    content_type = forms.ModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        label = 'Модели',
    )

    class Meta:
        model = PermissionProxy
        fields = '__all__'
