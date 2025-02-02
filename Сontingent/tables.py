from django_tables2 import tables
from Academhub.base import BaseTable
from Academhub.models import Qualification, Specialty, GroupStudents, Student

__all__ = (
    'GroupTable',
    'StudentTable',
    'SpecialtyTable',
    'QualificationTable',
)

class SpecialtyTable(BaseTable):
    class Meta:
        model = Specialty
        paginate_by = 10
        fields = ('pk', 'code', 'name')


class QualificationTable(BaseTable):
    specialty = tables.Column(
        accessor='specialty.name'
    )

    class Meta:
        model = Qualification
        paginate_by = 10
        fields = ('pk', 'short_name', 'name', 'specialty')


class GroupTable(tables.Table):
    qualification = tables.Column(accessor='qualification.name', 
        verbose_name='Квалификация')

    class Meta:
        model = GroupStudents
        paginate_by = 10
        fields = ('pk', 'number', 'qualification')


class StudentTable(BaseTable):
    group = tables.Column(
        verbose_name='Группы',
    )

    class Meta:
        model = Student
        paginate_by = 10
        fields = ('pk', 'full_name', 'phone', 'birth_date', 'course', 'group')