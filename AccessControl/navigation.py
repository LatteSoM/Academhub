from Academhub.models import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Панель администрации',
        sub_links=[
            ChildLink(
                name='Пользователи', 
                url='customuser_list',
                permission_required='customuser_view'
            ),
            ChildLink(
                name='Группы прав', 
                url='groupproxy_list',
                permission_required='groupproxy_list'
            ),
            ChildLink(
                name='Права', 
                url='permissionproxy_list',
                permission_required='permissionproxy_list'
            ),
        ]
    )
)