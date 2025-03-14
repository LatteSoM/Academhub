import django_tables2 as table
from Academhub.base import BaseTable, EmailColumn
from Academhub.models import CustomUser, GroupProxy, PermissionProxy

__all__ = (
    'UserTable',
    'GroupTable',
    'UserGroupTable',
    'PermissionTable',
)

class UserTable(BaseTable):
    email = EmailColumn(
        verbose_name='Почта'
    )

    user_permissions = table.ManyToManyColumn(
        verbose_name='Права'
    )
    
    groups = table.ManyToManyColumn(
        verbose_name='Группы прав'
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'user_permissions', 'groups', 'is_active', 'is_staff', 'is_teacher')


class GroupTable(BaseTable):
    permissions = table.ManyToManyColumn(
        verbose_name='Права'
    )

    class Meta:
        model = GroupProxy
        fields = ('name', 'permissions')


class GroupUserTable(BaseTable):
    
    email = EmailColumn(
        verbose_name='Почта'
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name',)


class PermissionTable(BaseTable):

    content_type = table.Column(
        verbose_name='Объект',
        accessor='content_type.app_labeled_name'
    )

    class Meta:
        model = PermissionProxy
        fields = ('name', 'content_type', 'codename')