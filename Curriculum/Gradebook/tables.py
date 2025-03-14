import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from Curriculum.base.tables.column import ActionColumn
from Curriculum.models import Gradebook, GradebookStudents


class BaseTable(tables.Table):
    """
    Базовая таблица
    """
    actions = ActionColumn([
        {'name': _('Detail'), 'url': 'detail'},
        {'name': _('Update'), 'url': 'update'},
        {'name': _('Delete'), 'url': 'delete'},
    ], verbose_name=_('Actions'))

    class Meta:
        attrs = {'class': 'table table-striped table-bordered table-hover'}


class BaseTable2(tables.Table):
    """
    Базовая таблица
    """
    actions = ActionColumn([
        {'name': _('Detail'), 'url': 'detail'},
        {'name': _('Update'), 'url': 'update'},
    ], verbose_name=_('Actions'))

    class Meta:
        attrs = {'class': 'table table-striped table-bordered table-hover'}


class GradebookTable(BaseTable):
    """
    Таблица ведомостей
    """
    group = tables.Column(verbose_name='Группа', accessor='group.name')
    curriculum_item = tables.Column(verbose_name='Дисциплина', accessor='curriculum_item.discipline.name')

    class Meta(BaseTable.Meta):
        model = Gradebook
        fields = ['group', 'curriculum_item', 'exam_date']


class TeacherGradeBookTable(BaseTable2):
    """
    Таблица ведомостей
    """
    group = tables.Column(verbose_name='Группа', accessor='group.name')
    curriculum_item = tables.Column(verbose_name='Дисциплина', accessor='curriculum_item.discipline.name')

    class Meta(BaseTable.Meta):
        model = Gradebook
        fields = ['group', 'curriculum_item', 'exam_date']


class GradebookTable2(BaseTable):
    """
    Таблица ведомостей
    """

    class Meta(BaseTable.Meta):
        model = Gradebook
        fields = ['id', 'group', 'teacher', 'exam_date']


class GradebookMobileTable(BaseTable):
    """
    Таблица ведомостей
    """
    group = tables.Column(verbose_name='Группа', accessor='group.name')
    curriculum_item = tables.Column(verbose_name='Дисциплина', accessor='curriculum_item.discipline.name')

    class Meta(BaseTable.Meta):
        model = Gradebook
        fields = ['group', 'curriculum_item', 'exam_date']


class GradebookStudentsTable(BaseTable):
    """
    Таблица ведомостей
    """
    student = tables.Column(verbose_name='Студент', accessor='student.get_full_name')

    class Meta(BaseTable.Meta):
        model = GradebookStudents
        fields = ['student', 'grade']


class GradebookTeachersTable(BaseTable):
    """
    Таблица ведомостей
    """

    class Meta(BaseTable.Meta):
        model = Gradebook
        fields = ['id', 'group', 'teacher', 'exam_date']