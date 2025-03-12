import django_tables2 as table
from django_tables2 import tables
from Academhub.base import BaseTable
from Academhub.models import Qualification, Specialty, GroupStudents, Student, Discipline, MiddleCertification, \
    ProfessionalModule, Practice, TermPaper, ContingentMovement

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
        table_name = 'Академический отпуск'
        fields = ('full_name', 'birth_date', 'group', 'left_course', 'academ_leave_date',
                  'academ_return_date', 'reason_of_academ')

class ExpulsionTable(BaseTable):
    specialty = tables.Column(accessor='group.qualification.specialty.code', verbose_name="Специальность")

    class Meta:
        model = Student
        paginate_by = 10
        table_name = 'Отчисленные'
        fields = ('date_of_expelling', 'reason_of_expelling', 'full_name', 'birth_date', 'specialty',
                  'group', 'education_base', 'education_basis', 'admission_order', 'transfer_to_2nd_year_order',
                  'transfer_to_3rd_year_order', 'transfer_to_4th_year_order', 'note', 'phone')


class ContingentColumn(tables.Column):
    def render(self, value):
        return value if value is not None else "-"

class StatisticksTable(tables.Table):
    index = tables.Column(empty_values=(), verbose_name="№ п/п")
    code = tables.Column(accessor='group.qualification.specialty.code', verbose_name="Код")
    specialty = tables.Column(accessor='group.qualification.specialty.name',
                              verbose_name="Направление подготовки/специальности")
    profile = tables.Column(accessor='group.qualification.name', verbose_name="Профиль")
    form = "Очная"
    basis = tables.Column(accessor='education_basis', verbose_name="Вид обучения")

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



    # Контингент по курсам
    year_1 = ContingentColumn(accessor='group.year_1_count', verbose_name="1 курс")
    year_2 = ContingentColumn(accessor='group.year_2_count', verbose_name="2 курс")
    year_3 = ContingentColumn(accessor='group.year_3_count', verbose_name="3 курс")
    year_4 = ContingentColumn(accessor='group.year_4_count', verbose_name="4 курс")

    # Академический отпуск
    academ_1 = ContingentColumn(accessor='group.academ_1_count', verbose_name="1 курс (акад)")
    academ_2 = ContingentColumn(accessor='group.academ_2_count', verbose_name="2 курс (акад)")
    academ_3 = ContingentColumn(accessor='group.academ_3_count', verbose_name="3 курс (акад)")

    total = tables.Column(accessor='group.total_students', verbose_name="ИТОГО")

    class Meta:
        model = Student
        template_name = "django_tables2/bootstrap.html"
        fields = ("index", "code", "specialty", "profile", "form", "basis",
                  "year_1", "year_2", "year_3", "year_4",
                  "academ_1", "academ_2", "academ_3", "total")
        attrs = {"class": "table table-striped"}

    def before_render(self, request):
        for index, row in enumerate(self.rows):
            row["index"] = index + 1



class ContingentMovementTable(tables.Table):
    class Meta:
        model = ContingentMovement
        template_name = "django_tables2/bootstrap4.html"
        fields = ("order_number", "action_type", "action_date", "previous_group", "new_group", "student")
        attrs = {"class": "table table-striped"}

