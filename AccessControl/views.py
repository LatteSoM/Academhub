from .form import *
from .table import UserTable, PermissionTable, GroupTable
from .filter import UserFilter, GroupFilter, PermissionFilter
from Academhub.models import CustomUser, PermissionProxy, GroupProxy
from Academhub.base import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView

# Create your views here.

#
## User
#

class UserTableView(ObjectTableView):
    table_class = UserTable
    filterset_class = UserFilter
    queryset = CustomUser.objects.all()

class UserDetailView(ObjectDetailView):
    model = CustomUser

class UserUpdateView(ObjectUpdateView):
    form_class = UserForm
    queryset = CustomUser.objects.all()

class UserCreateView(ObjectCreateView):
    model = CustomUser
    form_class = UserForm

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

#
## Group
#

class GroupTableView(ObjectTableView):
    table_class = GroupTable
    filterset_class = GroupFilter
    queryset = GroupProxy.objects.all()

    def get_model_name(self):
        return 'Группы прав'

class GroupDetailView(ObjectDetailView):
    model = GroupProxy

class  GroupUpdateView(ObjectUpdateView):
    form_class = GroupForm
    queryset = GroupProxy.objects.all()

class  GroupCreateView(ObjectCreateView):
    model = GroupProxy
    form_class = GroupForm