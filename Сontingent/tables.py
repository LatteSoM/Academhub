import django_tables2 as table
from django_tables2 import tables
from Academhub.base import BaseTable
from Academhub.models import Qualification, Specialty, GroupStudents, Student, Discipline

__all__ = (
    'GroupTable',
    'StudentTable',
    'StudentTable2',
    'SpecialtyTable',
    'DisciplineTable',
    'QualificationTable',
)

class DisciplineTable(BaseTable):
    specialty = tables.Column(
        accessor='specialty.name', 
    )

    class Meta:
        model = Discipline
        paginate_by = 10
        fields = (
            'name',
            'code',
            'specialty'
        )

class SpecialtyTable(BaseTable):
    class Meta:
        model = Specialty
        paginate_by = 10
        fields = ('code', 'name')


class QualificationTable(BaseTable):
    specialty = tables.Column(
        accessor='specialty.name'
    )

    class Meta:
        model = Qualification
        paginate_by = 10
        fields = ('short_name', 'name', 'specialty')


class GroupTable(BaseTable):
    qualification = tables.Column(accessor='qualification.name', 
        verbose_name='Квалификация')

    class Meta:
        model = GroupStudents
        paginate_by = 10
        fields = ('full_name', 'qualification')


class StudentTable(BaseTable):
    group = tables.Column(
        verbose_name='Группы',
    )

    class Meta:
        model = Student
        paginate_by = 10
        fields = ('full_name', 'phone', 'birth_date', 'course', 'group')

class StudentTable2(BaseTable):
    class Meta:
        model = Student
        paginate_by=30
        fields = ('full_name', 'course',)

class AcademTable(BaseTable):

    class Meta:
        model = Student
        paginate_by = 10
        table_name = ' Академический отпуск'
        fields = ('full_name', 'birth_date', 'group', 'left_course', 'academ_leave_date',
                  'academ_return_date', 'reason_of_academ')


