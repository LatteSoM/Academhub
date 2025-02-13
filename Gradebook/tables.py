from django_tables2 import tables

from Academhub.base import BaseTable
from Academhub.models import *

__all__ = (
    'GradebookTable',
)


class GradebookTable(BaseTable):
    teacher = tables.Column(
        verbose_name='Учитель'
    )

    group = tables.Column(
        verbose_name='Группа'
    )

    discipline = tables.Column(
        verbose_name='Дисциплина'
    )

    class Meta:
        model = Gradebook
        paginate_by=30
        fields = ('pk', 'teacher', 'number', 'name', 'group', 'discipline', 'status')