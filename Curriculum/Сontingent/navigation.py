from django.urls import reverse_lazy

from Curriculum.base.navigation import Navigation, ParentLink, ChildLink

NAVIGATION = Navigation(
    links=[
        ParentLink(
            name='Дисциплины',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('discipline_list')
                ),
                ChildLink(
                    name='Создать',
                    url=reverse_lazy('discipline_create')
                ),
            ]
        ),
        ParentLink(
            name='Специальности',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('specialty_list')
                ),
                ChildLink(
                    name='Создать',
                    url=reverse_lazy('specialty_create')
                ),
            ]
        ),
        ParentLink(
            name='Квалификации',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('qualification_list')
                ),
                ChildLink(
                    name='Создать',
                    url=reverse_lazy('qualification_create')
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
            name='Студенты',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('student_list')
                ),
                ChildLink(
                    name='Создать',
                    url=reverse_lazy('student_create')
                ),
                ChildLink(
                    name='Импорт',
                    url=reverse_lazy('import_students')
                ),
            ]
        ),
        ParentLink(
            name='Академические отпуска',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('academ_list')
                ),
            ]
        ),
        ParentLink(
            name='Отчисления',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('expulsion_list')
                ),
            ]
        ),
        ParentLink(
            name='Движение контингента',
            sub_links=[
                ChildLink(
                    name='Список',
                    url=reverse_lazy('contingent_movement_list')
                ),
            ]
        ),
        ParentLink(
            name='Статистика',
            sub_links=[
                ChildLink(
                    name='Просмотр',
                    url=reverse_lazy('statisticks')
                ),
            ]
        ),
    ]
)