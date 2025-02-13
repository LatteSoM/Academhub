from Academhub.base import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Ведомости',
        sub_links=[
            ChildLink('Все ведомости', 'gradebook_list'),
        ]
    )
)