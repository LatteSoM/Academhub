from Academhub.models import Navigation, ParentLink, ChildLink
from Academhub.utils import getpattern

navigation = Navigation(
    ParentLink(
        'Учебные планы',
        sub_links=[
            ChildLink('Учебные планы', 'curriculum_list'),
            ChildLink("Укомплектация учебных планов", 'curriculum_complete_set'),
            ChildLink("Выписки из учебных планов", getpattern('ReleaseFromCurriculum', 'detail')),
        ]
    )
)