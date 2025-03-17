from Academhub.models import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Ведомости',
        sub_links=[
            ChildLink(
                name='Текущие ведомости',
                url='gradebook_list',
                permission_required='gradebook_view',
            ),
            ChildLink(
                name='Ваши ведомости', 
                url="gradebookteacher_list",
                permission_required='gradebook_view',
            ),
            ChildLink(
                name='Закрытые ведомости',
                url="gradebookclosed_list",
                permission_required='gradebook_view',
            )
        ]
    )
)