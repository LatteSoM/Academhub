from Academhub.base import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Контингент',
        sub_links=[
            ChildLink('Специализации', 'specialty_list'),
            ChildLink('Квалификации', 'qualification_list'),
            ChildLink('Группы', 'groupstudents_list'),
            ChildLink('Студенты', 'student_list'),
            ChildLink('Дисциплины', 'discipline_list'),
            ChildLink('Академический отпуск', 'academ_list'),
            ChildLink('Движение контингента', 'expelled_students')
        ]
    )
)