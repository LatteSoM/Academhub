from Academhub.models import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Учебные планы',
        sub_links=[
            ChildLink('Учебные планы', 'curriculum_list')
        ]
    )
)