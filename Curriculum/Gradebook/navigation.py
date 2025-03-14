from django.urls import reverse_lazy

from Curriculum.base.navigation import Navigation, ParentLink, ChildLink

NAVIGATION = Navigation(
    links=[
        ParentLink(
            name='Ведомости',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('gradebook_list')
                ),
                ChildLink(
                    name='Создать',
                    url=reverse_lazy('gradebook_create')
                ),
            ]
        ),
        ParentLink(
            name='Преподаватели',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('gradebook_teachers_list')
                ),
            ]
        ),
    ]
)