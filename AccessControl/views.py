from .form import *
from .table import UserTable, PermissionTable, GroupTable
from .filter import UserFilter, GroupFilter, PermissionFilter
from Academhub.models import CustomUser, PermissionProxy, GroupProxy
from Academhub.base import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView

# Create your views here.

class PermissionMixin:
    '''
        Расширение для объектоа имеющие права доступа
    '''
    def get_permissions(self):
        '''
            Получение объекта прав
        '''
        pass
    
    def get_context_data(self, **kwargs):
        '''
            Добавляем в контекст права доступа
        '''
        context = super().get_context_data(**kwargs)
        permissions = self.get_permissions()
        context['permissions'] = permissions.as_context()
        return context

#
## User
#

class UserTableView(ObjectTableView):
    table_class = UserTable
    filterset_class = UserFilter
    queryset = CustomUser.objects.all()

class UserDetailView(PermissionMixin, ObjectDetailView):
    model = CustomUser
    template_name = 'AccessControl/detail/user_detail.html'

    fieldset = {
        'Пользовательская информация': [
            'email', 'full_name',
        ],
        'Системная информация': [
            'is_staff', 'is_teacher', 'is_active', 'last_login'
        ]
    }

    def get_permissions(self):
        return self.object.user_permissions.all()

class UserUpdateView(ObjectUpdateView):
    form_class = UserForm
    queryset = CustomUser.objects.all()

class UserCreateView(ObjectCreateView):
    model = CustomUser
    form_class = UserForm

#
## Group
#

class GroupTableView(ObjectTableView):
    table_class = GroupTable
    filterset_class = GroupFilter
    queryset = GroupProxy.objects.all()

    def get_model_name(self):
        return 'Группы прав'

class GroupDetailView(PermissionMixin, ObjectDetailView):
    model = GroupProxy

    def get_permissions(self):
        return PermissionProxy.objects.all()

class  GroupUpdateView(ObjectUpdateView):
    form_class = GroupForm
    queryset = GroupProxy.objects.all()

class  GroupCreateView(ObjectCreateView):
    model = GroupProxy
    form_class = GroupForm

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
