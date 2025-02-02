from Academhub.base import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Панель администрации',
        sub_links=[
            ChildLink('Пользователи', 'customuser_list'),
            ChildLink('Группы прав', 'groupproxy_list'),
            ChildLink('Права', 'permissionproxy_list'),
        ]
    )
)