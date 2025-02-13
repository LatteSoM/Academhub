from Academhub.base import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Контингент',
        sub_links=[
            ChildLink('Студенты', 'student_list'),
            ChildLink('Группы', 'groupstudents_list'),
            ChildLink('Квалификации', 'qualification_list'),
            ChildLink('Специализации', 'specialty_list'),
            ChildLink('Ведомости', 'gradebook_list'),
        ]
    )
)