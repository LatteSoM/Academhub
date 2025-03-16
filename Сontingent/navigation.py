from Academhub.models import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Контингент',
        sub_links=[
            ChildLink(
                name='Специализации', 
                url='specialty_list',
                permission_required='specialty_view'
            ),
            ChildLink(
                name='Квалификации', 
                url='qualification_list',
                permission_required='qualification_view'
            ),
            ChildLink(
                name='Группы', 
                url='groupstudents_list',
                permission_required='groupstudents_view'
            ),
            ChildLink(
                name='Студенты', 
                url='student_list',
                permission_required='student_view'
            ),
            ChildLink(
                name='Дисциплины', 
                url='discipline_list',
                permission_required='discipline_view'
            ),
            ChildLink(
                name='Академический отпуск', 
                url='academ_list',
            ),
            ChildLink(
                name='Движение контингента', 
                url='expelled_students',
            ),
            ChildLink(
                name='Статистика', 
                url='statisticks'
            ),
            ChildLink(
                name='Логи движений',
                url='contingent_movement_list'
            )
        ]
    )
)