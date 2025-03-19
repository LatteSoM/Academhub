from .form import *
from .mixin import PermissionMixin
from Academhub.models import Button
from Academhub.models import SubTable
from Academhub.utils import getpattern, getpermission
from .filter import UserFilter, GroupFilter, PermissionFilter
from Academhub.models import CustomUser, PermissionProxy, GroupProxy
from .table import UserTable, PermissionTable, GroupTable, GroupUserTable
from Academhub.generic import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView

__all__ = (
    'UserTableView',
    'UserDetailView',
    'UserUpdateView',
    'UserCreateView',
    
    'GroupTableView',
    'GroupDetailView',
    'GroupUpdateView',
    'GroupCreateView',

    'PermissionTableView',
    'PermissionDetailView',
    'PermissionUpdateView',
    'PermissionCreateView',
)

#
## User
#

class UserTableView(ObjectTableView):
    table_class = UserTable
    filterset_class = UserFilter
    queryset = CustomUser.objects.all()

    buttons = [
        Button (
            id='add',
            name = 'Добавить',
            link_name = getpattern(CustomUser, 'add'),
            permission = getpermission(CustomUser, 'add'),
        )
    ]

class UserDetailView(PermissionMixin, ObjectDetailView):
    model = CustomUser
    template_name = 'AccessControl/detail/user_detail.html'

    fieldset = {
        'Пользовательская информация': [
            'email', 
            'full_name',
            'is_staff', 
            'is_teacher', 
            'is_active', 
            'last_login'
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

    buttons = [
        Button (
            id='change',
            name = 'Обновить',
            link_params = ['pk'],
            link_name = getpattern(CustomUser, 'change'),
            permission= getpermission(CustomUser, 'change'),
        ),
        Button (
            id='to_list',
            name = 'К таблице',
            link_name = getpattern(CustomUser, 'list'),
            permission = getpermission(CustomUser, 'view'),
        )
    ]

    def get_permissions(self):
        return PermissionProxy.objects.filter(user__id=self.object.pk)

class UserUpdateView(ObjectUpdateView):
    form_class = UserUpdateForm
    queryset = CustomUser.objects.all()

    buttons = [
        Button (
            id='to_object',
            name = 'К объекту',
            link_params = ['pk'],
            link_name = getpattern(CustomUser, 'detail'),
            permission = getpermission(CustomUser, 'view'),
        ),
        Button (
            id='to_list',
            name = 'К таблице',
            link_name = getpattern(CustomUser, 'list'),
            permission = getpermission(CustomUser, 'view'),
        )
    ]

class UserCreateView(ObjectCreateView):
    model = CustomUser
    form_class = UserCreateForm

    buttons = [
        Button (
            id='to_list',
            name = 'К таблице',
            link_name = getpattern(CustomUser, 'list'),
            permission = getpermission(CustomUser, 'view'),
        )
    ]

#
## Group
#

class GroupTableView(ObjectTableView):
    table_class = GroupTable
    filterset_class = GroupFilter
    queryset = GroupProxy.objects.all()

    buttons = [
        Button (
            id='add',
            name = 'Добавить',
            link_name = getpattern(GroupProxy, 'add'),
            permission = getpermission(GroupProxy, 'add'),
        )
    ]

    def get_model_name(self):
        return 'Группы прав'

class GroupDetailView(PermissionMixin, ObjectDetailView):
    model = GroupProxy
    template_name = 'AccessControl/detail/group_detail.html'

    fieldset = {
        'Основная информация': [
            'name'
        ]
    }

    buttons = [
        Button(
            id = 'change',
            name = 'Обновить',
            link_params = ['pk'],
            link_name = getpattern(GroupProxy, 'change'),
            permission = getpermission(GroupProxy, 'change'),
        ),
        Button (
            id='to_list',
            name = 'К таблице',
            link_name = getpattern(GroupProxy, 'list'),
            permission = getpermission(GroupProxy, 'view'),
        )
    ]

    def custom_user_filter(object, queryset):
        return object.user_set.all()

    tables = [
        SubTable (
            name='Пользователи',
            queryset=CustomUser.objects.all(),
            table=GroupUserTable,
            filter_func=custom_user_filter
        )
    ]

    def get_permissions(self):
        return PermissionProxy.objects.filter(group__pk=self.object.pk)

class  GroupUpdateView(ObjectUpdateView):
    form_class = GroupForm
    queryset = GroupProxy.objects.all()

    buttons = [
        Button (
            id = 'to_object',
            name = 'К объекту',
            link_params = ['pk'],
            link_name = getpattern(GroupProxy, 'detail'),
            permission = getpermission(GroupProxy, 'view'),
        ),
        Button (
            id = 'to_list',
            name = 'К таблице', 
            link_name = getpattern(GroupProxy, 'list'),
            permission = getpermission(GroupProxy, 'view'),
        )
    ]

class  GroupCreateView(ObjectCreateView):
    model = GroupProxy
    form_class = GroupForm

    buttons = [
        Button (
            id = 'to_list',
            name = 'К таблице', 
            link_name = getpattern(GroupProxy, 'list'),
            permission = getpermission(GroupProxy, 'view'),
        )
    ]

#
## Permission
#

class PermissionTableView(ObjectTableView):
    table_class = PermissionTable
    filterset_class = PermissionFilter
    queryset = PermissionProxy.objects.all()

    def get_model_name(self):
        return 'Права'

class PermissionDetailView(ObjectDetailView):
    model = PermissionProxy

class PermissionUpdateView(ObjectUpdateView):
    form_class = PermissionForm
    queryset = PermissionProxy.objects.all()

    def get_model_name(self):
        return 'Права'

class PermissionCreateView(ObjectCreateView):
    model = PermissionProxy
    form_class = PermissionForm
