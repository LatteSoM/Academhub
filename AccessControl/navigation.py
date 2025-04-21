from Academhub.utils import getpermission, getpattern
from Academhub.models import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Панель администрации',
        sub_links=[
            ChildLink(
                name = 'Пользователи', 
                url = getpattern('CustomUser', 'list'),
                permission_required = getpermission('AccessControl', 'view_user')
            ),
            ChildLink(
                name='Группы прав', 
                url = getpattern('GroupProxy', 'list'),
                permission_required = getpermission('AccessControl', 'view_group')
            ),
            ChildLink(
                name='Права', 
                url = getpattern('PermissionProxy', 'list'),
                permission_required = getpermission('AccessControl', 'view_permission'),
            ),
            ChildLink (
                name='Админка',
                url = 'admin:index',
            )
        ]
    )
)