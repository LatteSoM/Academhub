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
            ParentLink(
                name='Студенты', 
                sub_links = [
                    ChildLink(
                        name='Текущие студенты',
                        url=getpattern('CurrentStudent', 'list'),
                        permission_required=getpermission('CurrentStudent', 'view')
                    ),
                    ChildLink(
                        name='Отчисленные студенты',
                        url=getpattern('ExpulsionStudent', 'list'),
                        permission_required=getpermission('ExpulsionStudent', 'view')
                    ),
                    ChildLink(
                        name='Студенты в академическом отпуске',
                        url=getpattern('AcademStudent', 'list'),
                        permission_required=getpermission('AcademStudent', 'view')
                    ),
                ]
            ),
            ChildLink(
                name='Дисциплины', 
                url=getpattern('Discipline', 'list'),
                permission_required=getpermission('Discipline', 'view')
            ),
            ChildLink(
                name='Статистика', 
                url='statisticks',
                permission_required=getpermission('Student', 'statistic')
            ),
            ChildLink(
                name='Логи движений',
                url=getpattern('ContingentMovement', 'list'),
                permission_required=getpermission('ContingentMovement', 'view')
            )
        ]
    )
)