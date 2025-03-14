import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from Curriculum.base.tables.column import ActionColumn
# from Curriculum.models import CustomUser, GroupProxy, PermissionProxy


class BaseTable(tables.Table):
    """
    Базовая таблица
    """
    actions = ActionColumn([
        {'name': _('Detail'), 'url': 'detail'},
        {'name': _('Update'), 'url': 'update'},
        {'name': _('Delete'), 'url': 'delete'},
    ], verbose_name=_('Actions'))

    class Meta:
        attrs = {'class': 'table table-striped table-bordered table-hover'}

# TODO: Update table classes to use new models.
# class UserTable(BaseTable):
#     """
#     Таблица пользователей
#     """
#
#     class Meta(BaseTable.Meta):
#         model = CustomUser
#         fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
#
#
# class GroupTable(BaseTable):
#     """
#     Таблица групп
#     """
#
#     class Meta(BaseTable.Meta):
#         model = GroupProxy
#         fields = ['id', 'name']
#
#
# class GroupUserTable(BaseTable):
#     """
#     Таблица пользователей группы
#     """
#
#     class Meta(BaseTable.Meta):
#         model = CustomUser
#         fields = ['id', 'email', 'first_name', 'last_name']
#
#
# class PermissionTable(BaseTable):
#     """
#     Таблица прав доступа
#     """
#
#     class Meta(BaseTable.Meta):
#         model = PermissionProxy
#         fields = ['id', 'name', 'codename', 'content_type']