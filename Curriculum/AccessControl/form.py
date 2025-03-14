# TODO: Update forms to use new models.
# from django import forms
# from django.contrib.auth.forms import SetPasswordForm
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth.models import Group
# from Curriculum.models import CustomUser, PermissionProxy, GroupProxy
# from Curriculum.base.forms.widgets.permission import PermissionsSelectMultiple
#
#
# class UserPasswordChangeForm(SetPasswordForm):
#     """
#     Форма для смены пароля пользователя.
#     """
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['new_password1'].help_text = ''
#
#
# class UserCreateForm(forms.ModelForm):
#     """
#     Форма для создания пользователя.
#     """
#     password = forms.CharField(widget=forms.PasswordInput)
#     groups = forms.ModelMultipleChoiceField(
#         queryset=GroupProxy.objects.all(),
#         widget=PermissionsSelectMultiple(queryset=GroupProxy.objects.all()),
#         required=False
#     )
#
#     class Meta:
#         model = CustomUser
#         fields = ['email', 'first_name', 'last_name', 'password', 'groups', 'is_active', 'is_staff', 'is_superuser']
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#             self.save_m2m()
#         return user
#
#
# class UserUpdateForm(forms.ModelForm):
#     """
#     Форма для обновления пользователя.
#     """
#     groups = forms.ModelMultipleChoiceField(
#         queryset=GroupProxy.objects.all(),
#         widget=PermissionsSelectMultiple(queryset=GroupProxy.objects.all()),
#         required=False
#     )
#
#     class Meta:
#         model = CustomUser
#         fields = ['email', 'first_name', 'last_name', 'groups', 'is_active', 'is_staff', 'is_superuser']
#
#
# class GroupForm(forms.ModelForm):
#     """
#     Форма для группы.
#     """
#     permissions = forms.ModelMultipleChoiceField(
#         queryset=PermissionProxy.objects.all(),
#         widget=PermissionsSelectMultiple(queryset=PermissionProxy.objects.all()),
#         required=False
#     )
#
#     class Meta:
#         model = GroupProxy
#         fields = ['name', 'permissions']
#
#
# class PermissionForm(forms.ModelForm):
#     """
#     Форма для прав доступа
#     """
#
#     class Meta:
#         model = PermissionProxy
#         fields = '__all__'