from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# from django.contrib.auth.views import PasswordChangeView
# from django.contrib.messages.views import SuccessMessageMixin
# from django.urls import reverse_lazy
# from django_filters.views import FilterView
# from django_tables2 import SingleTableMixin, SingleTableView

# from Curriculum.AccessControl.filter import UserFilter, GroupFilter, PermissionFilter
# from Curriculum.AccessControl.form import UserCreateForm, UserUpdateForm, GroupForm, \
#     UserPasswordChangeForm, PermissionForm
# from Curriculum.AccessControl.table import UserTable, GroupTable, PermissionTable, GroupUserTable
from Curriculum.base.generic import ObjectCreateView, ObjectUpdateView, ObjectDetailView, ObjectListView, \
    ObjectTemplateView
# from Curriculum.models import CustomUser, GroupProxy, PermissionProxy


class PermissionMixin(LoginRequiredMixin):
    """
    Миксин для проверки прав доступа.
    """

    def get_permissions(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_permissions()
        return context

# TODO: Update view classes to use new models.
# class UserTableView(SingleTableMixin, FilterView):
#     """
#     Представление для отображения таблицы пользователей.
#     """
#     table_class = UserTable
#     model = CustomUser
#     template_name = 'AccessControl/list/user_list.html'
#     filterset_class = UserFilter
#
#
# class UserDetailView(PermissionMixin, ObjectDetailView):
#     """
#     Представление для отображения детальной информации о пользователе.
#     """
#     model = CustomUser
#     template_name = 'AccessControl/detail/user_detail.html'
#
#     def get_permissions(self):
#         return [
#             ('change_user', _('Can change user')),
#             ('delete_user', _('Can delete user')),
#         ]
#
#
# class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
#     """
#     Представление для смены пароля пользователя.
#     """
#     template_name = 'base_update.html'
#     form_class = UserPasswordChangeForm
#     success_message = 'Пароль успешно изменен'
#
#     def get_success_url(self):
#         return reverse_lazy('user_detail', kwargs={'pk': self.request.user.pk})
#
#
# class UserUpdateView(ObjectUpdateView):
#     """
#     Представление для обновления пользователя.
#     """
#     model = CustomUser
#     form_class = UserUpdateForm
#     template_name = 'AccessControl/update/user_form.html'
#
#
# class UserCreateView(ObjectCreateView):
#     """
#     Представление для создания пользователя.
#     """
#     model = CustomUser
#     form_class = UserCreateForm
#     template_name = 'AccessControl/create/user_form.html'
#
#
# class GroupTableView(ObjectTableView):
#     """
#     Представление для отображения таблицы групп.
#     """
#     table_class = GroupTable
#     model = GroupProxy
#     template_name = 'AccessControl/list/group_list.html'
#     filterset_class = GroupFilter
#
#     def get_model_name(self):
#         return 'Группа'
#
#
# class GroupDetailView(PermissionMixin, ObjectDetailView):
#     """
#     Представление для отображения детальной информации о группе.
#     """
#     model = GroupProxy
#     template_name = 'AccessControl/detail/group_detail.html'
#     sub_tables = []
#
#     def custom_user_filter(object, queryset):
#         return queryset.filter(groups=object)
#
#     sub_tables = [
#         {
#             'table': GroupUserTable,
#             'queryset': CustomUser.objects.all(),
#             'name': 'Пользователи',
#             'filter_key': 'group',
#             'filter_func': custom_user_filter
#         },
#     ]
#
#     def get_permissions(self):
#         return [
#             ('change_group', _('Can change group')),
#             ('delete_group', _('Can delete group')),
#         ]
#
#
# class GroupUpdateView(ObjectUpdateView):
#     """
#     Представление для обновления группы.
#     """
#     model = GroupProxy
#     form_class = GroupForm
#     template_name = 'AccessControl/update/group_form.html'
#
#
# class GroupCreateView(ObjectCreateView):
#     """
#     Представление для создания группы.
#     """
#     model = GroupProxy
#     form_class = GroupForm
#     template_name = 'AccessControl/create/group_form.html'
#
#
# class PermissionTableView(ObjectTableView):
#     """
#     Представление для отображения таблицы прав доступа.
#     """
#     table_class = PermissionTable
#     model = PermissionProxy
#     template_name = 'AccessControl/list/permission_list.html'
#     filterset_class = PermissionFilter
#
#     def get_model_name(self):
#         return 'Права доступа'
#
#
# class PermissionDetailView(ObjectDetailView):
#     """
#     Представление для отображения детальной информации о праве доступа.
#     """
#     model = PermissionProxy
#     template_name = 'AccessControl/detail/permission_detail.html'
#
#
# class PermissionUpdateView(ObjectUpdateView):
#     """
#     Представление для обновления права доступа.
#     """
#     model = PermissionProxy
#     form_class = PermissionForm
#     template_name = 'AccessControl/update/permission_form.html'
#
#     def get_model_name(self):
#         return 'Права доступа'
#
#
# class PermissionCreateView(ObjectCreateView):
#     """
#     Представление для создания права доступа.
#     """
#     model = PermissionProxy
#     form_class = PermissionForm
#     template_name = 'AccessControl/create/permission_form.html'