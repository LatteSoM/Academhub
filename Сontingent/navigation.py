from Academhub.utils import getpermission, getpattern
from Academhub.models import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Контингент',
        sub_links=[
            ChildLink(
                name='Специализации', 
                url=getpattern('Specialty', 'list'),
                permission_required=getpermission('Сontingent', 'view_specialty')
            ),
            ChildLink(
                name='Квалификации', 
                url=getpattern('Qualification', 'list'),
                permission_required=getpermission('Сontingent', 'view_qualification')
            ),
            ChildLink(
                name='Группы', 
                url=getpattern('GroupStudents', 'list'),
                permission_required=getpermission('Сontingent', 'view_group_student')
            ),
            ParentLink(
                name='Студенты', 
                sub_links = [
                    ChildLink(
                        name='Текущие студенты',
                        url=getpattern('CurrentStudent', 'list'),
                        permission_required=getpermission('Сontingent', 'view_current_student')
                    ),
                    ChildLink(
                        name='Отчисленные студенты',
                        url=getpattern('ExpulsionStudent', 'list'),
                        permission_required=getpermission('Сontingent', 'view_expulsion_student')
                    ),
                    ChildLink(
                        name='Студенты в академическом отпуске',
                        url=getpattern('AcademStudent', 'list'),
                        permission_required=getpermission('Сontingent', 'view_academ_student')
                    ),
                    ChildLink(
                        name='Перевод на курс',
                        url='transfer_students_form',
                        permission_required=getpermission('Сontingent', 'transfer_students')
                    ),
                ]
            ),
            ChildLink(
                name='Дисциплины', 
                url=getpattern('Discipline', 'list'),
                permission_required=getpermission('Сontingent', 'view_discipline')
            ),
            ChildLink(
                name='Статистика', 
                url='statisticks',
                permission_required=getpermission('Сontingent', 'view_statistic')
            ),
            ChildLink(
                name='Логи движений',
                url=getpattern('ContingentMovement', 'list'),
                permission_required=getpermission('Сontingent', 'view_movement')
            )
        ]
    )
)