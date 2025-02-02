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

    class Meta:
        model = CustomUser
        fields = ('pk', 'email', 'full_name', 'is_active', 'is_staff', 'is_teacher')


class GroupTable(BaseTable):
    permissions = table.ManyToManyColumn(
        verbose_name='Права'
    )

    class Meta:
        model = PermissionProxy
        fields = ('pk', 'name', 'permissions')


class PermissionTable(BaseTable):
    class Meta:
        model = GroupProxy
        fields = ('pk', 'name', 'content_type', 'codename')