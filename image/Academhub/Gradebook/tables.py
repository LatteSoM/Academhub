import django_tables2 as table
from django_tables2 import tables

from Academhub.models import Gradebook, GradebookStudents, CustomUser
from Academhub.tables import BaseTable, BaseTable2

__all__ = (
    'GradebookTable',
    'GradebookTable2',
    'GradebookMobileTable',
    'GradebookTeachersTable',
    'GradebookStudentsTable',
)


STATUS_CLASS_MAP = {
    'Не заполнена': 'status-not-filled',
    'Открыта': 'status-opened',
    'Заполнена': 'status-filled',
    'Закрыта': 'status-closed',
    'Просрочена': 'status-overdue',
}

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
        paginate_by = 30
        fields = ('name', 'teachers', 'group', 'discipline', 'status', 'type_of_grade_book')
        row_attrs = {
            "class": lambda record: STATUS_CLASS_MAP.get(record.status, 'status-unknown')
        }


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
        row_attrs = {
            "class": lambda record: STATUS_CLASS_MAP.get(record.status, 'status-unknown')
        }


class GradebookMobileTable(BaseTable):
    teachers = table.ManyToManyColumn(verbose_name='Учителя')
    group = tables.Column(verbose_name='Группа')

    class Meta:
        model = Gradebook
        paginate_by = 30
        fields = ('pk', 'teachers', 'group')  # Только ключевые колонки
        row_attrs = {
            "class": lambda record: STATUS_CLASS_MAP.get(record.status, 'status-unknown')
        }


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