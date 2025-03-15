from Academhub.models import Navigation, ParentLink, ChildLink

navigation = Navigation(
    ParentLink(
        'Ведомости',
        sub_links=[
            ChildLink('Все ведомости', 'gradebook_list'),
            ChildLink('Ваши ведомости', "gradebookteacher_list")
        ]
    )
)