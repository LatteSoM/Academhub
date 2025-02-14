from django_tables2 import tables

from Academhub.base import BaseTable
from Academhub.models import Gradebook, GradebookStudents

__all__ = (
    'GradebookTable',
    'GradebookStudentsTable'
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
        fields = ('name', 'teacher', 'group', 'discipline', 'status')


class GradebookStudentsTable(BaseTable):
    student = tables.Column(verbose_name='Студент')

    class Meta:
        model = GradebookStudents
        paginate_by=30
        fields = ('student', 'ticket_number', 'grade')