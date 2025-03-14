import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from Curriculum.base.tables.column import ActionColumn
from Curriculum.models import Discipline, Qualification, Specialty, GroupStudents, Student, ContingentMovement, \
    MiddleCertification, ProfessionalModule, Practice, TermPaper


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


class DisciplineTable(BaseTable):
    """
    Таблица дисциплин
    """

    class Meta(BaseTable.Meta):
        model = Discipline
        fields = ('name',)


class SpecialtyTable(BaseTable):
    """
    Таблица специальностей
    """

    class Meta(BaseTable.Meta):
        model = Specialty
        fields = ('code', 'name')


class QualificationTable(BaseTable):
    """
    Таблица квалификаций
    """

    class Meta(BaseTable.Meta):
        model = Qualification
        fields = ('code', 'name')


class GroupTable(BaseTable):
    """
    Таблица групп
    """
    year = tables.Column(verbose_name='Год поступления', accessor='year')

    class Meta(BaseTable.Meta):
        model = GroupStudents
        fields = ('name', 'curriculum', 'start_date', 'end_date', 'year')


class StudentTable(BaseTable):
    """
    Таблица студентов
    """

    class Meta(BaseTable.Meta):
        model = Student
        fields = ('last_name', 'first_name', 'middle_name', 'birth_date', 'group')


class StudentTable2(BaseTable):
    """
    Таблица студентов
    """

    class Meta(BaseTable.Meta):
        model = Student
        fields = ('last_name', 'first_name', 'middle_name', 'birth_date', 'group')


class AcademTable(BaseTable):
    """
    Таблица академических отпусков
    """

    class Meta(BaseTable.Meta):
        model = Student
        fields = ('last_name', 'first_name', 'middle_name', 'birth_date', 'group')


class ExpulsionTable(BaseTable):
    """
    Таблица отчисленных студентов
    """

    class Meta(BaseTable.Meta):
        model = Student
        fields = ('last_name', 'first_name', 'middle_name', 'birth_date', 'group')


class ContingentColumn(tables.Column):
    def render(self, value):
        if value == 'academ_leave':
            return format_html('<span class="badge bg-warning">Академический отпуск</span>')
        elif value == 'expelled':
            return format_html('<span class="badge bg-danger">Отчислен</span>')
        elif value == 'recovered':
            return format_html('<span class="badge bg-success">Восстановлен</span>')
        elif value == 'academ_return':
            return format_html('<span class="badge bg-info">Вернулся из академического отпуска</span>')
        else:
            return format_html('<span class="badge bg-secondary">Неизвестно</span>')


class StatisticksTable(tables.Table):
    group = tables.Column(verbose_name='Группа', accessor='group__name')
    count = tables.Column(verbose_name='Количество')
    type = ContingentColumn(verbose_name='Тип')


class MiddleCertificationTable(BaseTable):
    """
    Таблица промежуточных аттестаций
    """

    class Meta(BaseTable.Meta):
        model = MiddleCertification
        fields = ('name', 'is_exam')

    def render_is_exam(self, value):
        if value:
            return format_html('<span class="badge bg-success">Да</span>')
        else:
            return format_html('<span class="badge bg-danger">Нет</span>')


class ProfessionalModuleTable(BaseTable):
    """
    Таблица профессиональных модулей
    """

    class Meta(BaseTable.Meta):
        model = ProfessionalModule
        fields = ('name',)


class PracticeTable(BaseTable):
    """
    Таблица практик
    """

    class Meta(BaseTable.Meta):
        model = Practice
        fields = ('name', 'practice_type')

    def render_practice_type(self, value):
        if value == 'educational':
            return format_html('<span class="badge bg-success">Учебная</span>')
        elif value == 'production':
            return format_html('<span class="badge bg-primary">Производственная</span>')
        else:
            return format_html('<span class="badge bg-secondary">Неизвестно</span>')


class TermPaperTable(BaseTable):
    """
    Таблица курсовых работ
    """

    class Meta:
        model = TermPaper
        fields = ('topic',)
        template_name = "django_tables2/bootstrap4.html"
        attrs = {"class": "table table-striped table-bordered table-hover"}

    def before_render(self, request):
        self.columns.hide('id')


class ContingentMovementTable(tables.Table):
    """
    Таблица движения контингента студентов
    """
    student = tables.Column(verbose_name='Студент', accessor='student.get_full_name')
    type = ContingentColumn(verbose_name='Тип')

    class Meta:
        model = ContingentMovement
        fields = ('student', 'order_number', 'order_date', 'type')