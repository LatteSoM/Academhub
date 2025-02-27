from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField

class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={"autofocus": True}),
        label='Почта'
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )