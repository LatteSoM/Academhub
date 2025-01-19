from .base_navigation import *

navigation = Navigation(
    ChildLink(
        'Home',
        'home'
    )
)

# Пример навигации

# navigation = Navigation(
#     ParentLink(
#         'Test',
#         sub_links=[
#             ChildLink('Home', 'home'),
#             ParentLink(
#                 'What',
#                 sub_links=[
#                     ChildLink('Home', 'home'),
#                     ChildLink('About', 'home'),
#                     ParentLink(
#                         'Test',
#                         sub_links= []
#                     )
#                 ]
#             )
#         ]
#     )
# )