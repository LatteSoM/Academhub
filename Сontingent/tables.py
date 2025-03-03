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



from Academhub.models import MiddleCertification, ProfessionalModule, Practice, TermPaper


class MiddleCertificationTable(BaseTable):
    class Meta:
        model = MiddleCertification
        template_name = "django_tables2/bootstrap4.html"  # Или 'inc/table/table.html'
        fields = ("semester", "discipline.name", "hours", "is_exam")
        attrs = {"class": "table table-striped"}

    is_exam = tables.Column(verbose_name="Тип", accessor="is_exam", orderable=False,
                            empty_values=(), attrs={"td": {"class": "text-center"}})

    def render_is_exam(self, value):
        return "Экзамен" if value else "Зачет"


class ProfessionalModuleTable(BaseTable):
    class Meta:
        model = ProfessionalModule
        template_name = "django_tables2/bootstrap4.html"
        fields = ("module_name", "hours")
        attrs = {"class": "table table-striped"}


class PracticeTable(BaseTable):
    practice_type = tables.Column(verbose_name="Тип", accessor="practice_type")

    class Meta:
        model = Practice
        template_name = "django_tables2/bootstrap4.html"
        fields = ("practice_name", "hours", "semester", "practice_type")
        attrs = {"class": "table table-striped"}

    def render_practice_type(self, value):
        return dict(Practice.PRACTICE_TYPES).get(value, value)


class TermPaperTable(BaseTable):
    class Meta:
        model = TermPaper
        template_name = "django_tables2/bootstrap4.html"
        fields = ("discipline.name", "topic", "grade")
        attrs = {"class": "table table-striped"}



