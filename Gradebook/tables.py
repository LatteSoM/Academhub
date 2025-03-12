import django_tables2 as table
from django_tables2 import tables
from Academhub.base import BaseTable, BaseTable2
from Academhub.models import Gradebook, GradebookStudents, CustomUser

__all__ = (
    'GradebookTable',
    'GradebookTable2',
    'GradebookMobileTable',
    'GradebookTeachersTable',
    'GradebookStudentsTable',
)


class GradebookTable(BaseTable):
    teachers = table.ManyToManyColumn(
        verbose_name='Учителя'
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
        fields = ('name', 'teachers', 'group', 'discipline', 'status')



class TeacherGradeBookTable(BaseTable2):
    group = tables.Column(
        verbose_name='Группа'
    )

    discipline = tables.Column(
        verbose_name='Дисциплина'
    )
    class Meta:
        model = Gradebook
        fields = ('name', 'group', 'discipline')



class GradebookTable2(BaseTable):
    teachers = table.ManyToManyColumn(
        verbose_name='Учителя'
    )

    discipline = tables.Column(
        verbose_name='Дисциплина'
    )

    class Meta:
        model = Gradebook
        paginate_by=30
        fields = ('name', 'teachers', 'discipline', 'status')


class GradebookMobileTable(BaseTable):
    teachers = table.ManyToManyColumn(verbose_name='Учителя')
    group = tables.Column(verbose_name='Группа')

    class Meta:
        model = Gradebook
        paginate_by = 30
        fields = ('pk', 'teachers', 'group')  # Только ключевые колонки


class GradebookStudentsTable(BaseTable):
    student = tables.Column(verbose_name='Студент')

    class Meta:
        model = GradebookStudents
        paginate_by=30
        fields = ('student', 'ticket_number', 'grade')


class GradebookTeachersTable(BaseTable):
    class Meta:
        model = CustomUser
        paginate_by=30
        fields = ('full_name', )