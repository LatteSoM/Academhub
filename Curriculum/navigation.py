from Academhub.base import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Учебные планы',
        sub_links=[
            ChildLink('Учебные планы', 'curriculums_list')
        ]
    )
)