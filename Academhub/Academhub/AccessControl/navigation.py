from Academhub.utils import getpermission, getpattern
from Academhub.models import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Панель администрации',
        sub_links=[
            ChildLink(
                name = 'Пользователи', 
                url = getpattern('CustomUser', 'list'),
                permission_required = getpermission('CustomUser','view')
            ),
            ChildLink(
                name='Группы прав', 
                url = getpattern('GroupProxy', 'list'),
                permission_required = getpermission('GroupProxy','view')
            ),
            ChildLink(
                name='Права', 
                url = getpattern('PermissionProxy', 'list'),
                permission_required = getpermission('PermissionProxy', 'view'),
            ),
            ChildLink (
                name='Админка',
                url = 'admin:index',
                admin = True
            )
        ]
    )
)