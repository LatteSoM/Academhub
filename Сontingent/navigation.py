from Academhub.base import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Контингент',
        sub_links=[
            ChildLink('Студенты', 'studentdto_list'),
            ChildLink('Группы', 'group_list'),
            ChildLink('Специализации', 'specialization_list'),
            ChildLink('Квалификации', 'qualification_list'),
        ]
    )
)