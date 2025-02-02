from django import forms
from Academhub.models import CustomUser, PermissionProxy, GroupProxy

class UserForm(forms.ModelForm):
    email = forms.EmailField(
        label='Почта',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'email@email.email'
            }
        )
    )

    full_name = forms.CharField(
        label='ФИО',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Иванов Иван Иванович'
            }
        )
    )


    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'is_staff', 'is_teacher']

class PermissionForm(forms.ModelForm):
    class Meta:
        model = PermissionProxy
        fields = '__all__'

class GroupForm(forms.ModelForm):
    class Meta:
        model = GroupProxy
        fields = '__all__'