from django_tables2 import tables
from Academhub.base import BaseTable
from .models import QualificationDTO, SpecializationDTO, GroupDTO, StudentDTO

__all__ = (
    'GroupTable',
    'StudentTable',
    'QualificationTable',
    'SpecializationTable',
)

class QualificationTable(BaseTable):
    class Meta:
        model = QualificationDTO
        paginate_by = 10
        fields = ('pk', 'union_name', 'name')

class SpecializationTable(BaseTable):
    class Meta:
        model = SpecializationDTO
        paginate_by = 10
        fields = ('pk', 'code', 'name')

class GroupTable(tables.Table):
    qualification = tables.Column(accessor='qualification.name', verbose_name='Квалификация')
    specialization = tables.Column(accessor='specialization.name', verbose_name='Специальность')

    class Meta:
        model = GroupDTO
        paginate_by = 10
        fields = ('pk', 'qualification', 'specialization')

class StudentTable(BaseTable):
    group = tables.Column(
        verbose_name='Группы',
    )

    class Meta:
        model = StudentDTO
        paginate_by = 10
        fields = ('pk', 'full_name', 'phone', 'birth_date', 'course', 'group')