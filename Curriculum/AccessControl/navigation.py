from django.urls import reverse_lazy
from Curriculum.base.navigation import ChildLink, ParentLink, Navigation

NAVIGATION = Navigation(
    links=[
        ParentLink(
            name='Пользователи',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('user_list')
                ),
                ChildLink(
                    name='Создать',
                    url=reverse_lazy('user_create')
                ),
            ]
        ),
        ParentLink(
            name='Группы',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('group_list')
                ),
                ChildLink(
                    name='Создать',
                    url=reverse_lazy('group_create')
                ),
            ]
        ),
        ParentLink(
            name='Права доступа',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('permission_list')
                ),
                ChildLink(
                    name='Создать',
                    url=reverse_lazy('permission_create')
                ),
            ]
        ),

    ]
)