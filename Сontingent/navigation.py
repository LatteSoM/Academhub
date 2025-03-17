from Academhub.utils import getpermission, getpattern
from Academhub.models import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Контингент',
        sub_links=[
            ChildLink(
                name='Специализации', 
                url=getpattern('Specialty', 'list'),
                permission_required=getpermission('Specialty', 'view')
            ),
            ChildLink(
                name='Квалификации', 
                url=getpattern('Qualification', 'list'),
                permission_required=getpermission('Qualification', 'view')
            ),
            ChildLink(
                name='Группы', 
                url=getpattern('GroupStudents', 'list'),
                permission_required=getpermission('GroupStudents', 'view')
            ),
            ChildLink(
                name='Студенты', 
                url=getpattern('Student', 'list'),
                permission_required=getpermission('Student', 'view')
            ),
            ChildLink(
                name='Дисциплины', 
                url=getpattern('Discipline', 'list'),
                permission_required=getpermission('Discipline', 'view')
            ),
            ChildLink(
                name='Академический отпуск', 
                url='academ_list',
            ),
            ChildLink(
                name='Движение контингента', 
                url=getpattern('ContingentMovement', 'list'),
                permission_required=getpermission('ContingentMovement', 'view')
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