from django_tables2 import tables

from Academhub.base import BaseTable
from Academhub.models import Gradebook, GradebookStudents

__all__ = (
    'GradebookTable2',
    'GradebookTable',
    'GradebookMobileTable',
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

class GradebookTable2(BaseTable):
    teacher = tables.Column(
        verbose_name='Учитель'
    )

    discipline = tables.Column(
        verbose_name='Дисциплина'
    )

    class Meta:
        model = Gradebook
        paginate_by=30
        fields = ('name', 'teacher', 'discipline', 'status')


class GradebookMobileTable(BaseTable):
    teacher = tables.Column(verbose_name='Учитель')
    group = tables.Column(verbose_name='Группа')

    class Meta:
        model = Gradebook
        paginate_by = 30
        fields = ('pk', 'teacher', 'group')  # Только ключевые колонки




class GradebookStudentsTable(BaseTable):
    student = tables.Column(verbose_name='Студент')

    class Meta:
        model = GradebookStudents
        paginate_by=30
        fields = ('student', 'ticket_number', 'grade')

