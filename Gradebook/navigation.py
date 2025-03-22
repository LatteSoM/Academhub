from Academhub.utils import getpermission, getpattern
from Academhub.models import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Ведомости',
        sub_links=[
            ChildLink(
                name='Все ведомости', 
                url=getpattern('Gradebook', 'list'),
                permission_required=getpermission('Gradebook', 'add'),
            ),
            ChildLink(
                name='Ваши ведомости', 
                url="gradebookteacher_list",
                permission_required=getpermission('Gradebook', 'view'),
            ),
            ChildLink(
                name='Закрытые ведомости',
                url="gradebookclosed_list",
                permission_required=getpermission('Gradebook', 'add'),
            ),
            ChildLink(
                name="Таблица оценок группы",
                url="gradebook_view_group_grades",
                permission_required=getpermission('Gradebook', 'add'),
            )
        ]
    )
)