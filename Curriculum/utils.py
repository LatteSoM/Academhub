from django.db import models

# TODO: Review this class after model changes.
# class UnifiedPermissionQyerySet(models.QuerySet):
#     """
#     Для унификации доступа к правам
#     """
#
#     def as_context(self) -> dict:
#         return {
#             'read': self.filter(codename__startswith='view_').values_list('codename', flat=True),
#             'add': self.filter(codename__startswith='add_').values_list('codename', flat=True),
#             'change': self.filter(codename__startswith='change_').values_list('codename', flat=True),
#             'delete': self.filter(codename__startswith='delete_').values_list('codename', flat=True),
#         }