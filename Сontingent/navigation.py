from Academhub.base import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Контингент',
        sub_links=[
            ChildLink('Студенты', 'student_list'),
            ChildLink('Группы', 'groupstudents_list'),
            ChildLink('Специализации', 'specialization_list'),
            ChildLink('Квалификации', 'qualification_list'),
        ]
    )
)