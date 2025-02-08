import django_tables2 as table
from Academhub.base import BaseTable, EmailColumn
from Academhub.models import CustomUser, GroupProxy, PermissionProxy

__all__ = (
    'UserTable',
    'GroupTable',
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
        fields = ('pk', 'email', 'full_name', 'user_permissions', 'groups', 'is_active', 'is_staff', 'is_teacher')


class GroupTable(BaseTable):
    permissions = table.ManyToManyColumn(
        verbose_name='Права'
    )

    class Meta:
        model = GroupProxy
        fields = ('pk', 'name', 'permissions')


class PermissionTable(BaseTable):

    content_type = table.Column(
        verbose_name='Объект',
        accessor='content_type.app_labeled_name'
    )

    class Meta:
        model = PermissionProxy
        fields = ('pk', 'name', 'content_type', 'can_add', 'can_view', 'can_delete', 'can_change')