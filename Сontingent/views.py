from .forms import *
from .tables import *
from .filters import *
from Gradebook.tables import GradebookTable2
from Academhub.base import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView
from Academhub.models import GroupStudents, Discipline, Qualification, Specialty, Student, Gradebook

__all__ = (
    'DisciplineTableView',
    'DisciplineDetailView',
    'DisciplineUpdateView',
    'DisciplineCreateView',

    'SpecialtyTableView',
    'SpecialtyDetailView',
    'SpecialtyUpdateView',
    'SpecialtyCreateView',

    'StudentTableView', 
    'StudentDetailView', 
    'StudentUpdateView', 
    'StudentCreateView',

    'GroupTableView', 
    'GroupDetailView', 
    'GroupUpdateView', 
    'GroupCreateView',

    'QualificationTableView',
    'QualificationCreateView',
    'QualificationDetailView',
    'QualificationUpdateView'
)

#
## Discipline
#

class DisciplineTableView(ObjectTableView):
    """
        Класс для отображения таблицы дисциплин.
    """
    table_class = DisciplineTable
    filterset_class = DisciplineFilter
    queryset = Discipline.objects.all()

class DisciplineDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации о дисциплине.
    """
    model= Discipline
    paginate_by  = 30
    fieldset = {
        'Основная информация':
            ['name', 'code', 'specialty',]
    }
        
class DisciplineUpdateView(ObjectUpdateView):
    """
    Класс для обновления информации о дисциплине.
    """
    form_class = DisciplineForm
    queryset = Discipline.objects.all()
    
class DisciplineCreateView(ObjectCreateView):
    """
    Класс для создания новой дисциплины.
    """
    model = Discipline
    form_class = DisciplineForm

#
## Specialty
#

class SpecialtyTableView(ObjectTableView):
    """
    Класс для отображения таблицы специальностей.
    """
    table_class = SpecialtyTable
    filterset_class = SpecialtyFilter
    queryset = Specialty.objects.all()

class SpecialtyDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации о специальности.
    """
    model= Specialty
    paginate_by  = 30
    template_name = 'Contingent/detail/specialty_detail.html'

    fieldset = {
        'Основная информация':
            ['code', 'name'],
    }

    def get_tables(self):
        students = Qualification.objects.filter(specialty__pk=self.object.pk)
        table = QualificationTable(data=students)
        return [table]

class SpecialtyUpdateView(ObjectUpdateView):
    """
    Класс для обновления информации о специальности.
    """
    form_class = SpecialtyForm
    queryset = Specialty.objects.all()

class SpecialtyCreateView(ObjectCreateView):
    """
    Класс для создания новой специальности.
    """
    model = Specialty
    form_class = SpecialtyForm

#
## Qualification
#

class QualificationTableView(ObjectTableView):
    """
    Класс для отображения таблицы квалификаций.
    """
    table_class = QualificationTable
    filterset_class = QualificationFilter
    queryset = Qualification.objects.all()

class QualificationTableView(ObjectTableView):
    """
    Класс для отображения таблицы квалификаций.
    """
    table_class = QualificationTable
    filterset_class = QualificationFilter
    queryset = Qualification.objects.all()

class QualificationDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации о квалификации.
    """
    model= Qualification
    paginate_by  = 30
    template_name = 'Contingent/detail/qualification_detail.html'

    fieldset = {
        'Основная информация':
            ['short_name', 'name', 'specialty']
    }

    def get_tables(self):
        students = GroupStudents.objects.filter(qualification__pk=self.object.pk)
        table = GroupTable(data=students)
        return [table]

class QualificationUpdateView(ObjectUpdateView):
    """
    Класс для обновления информации о квалификации.
    """
    form_class = QualificationForm
    queryset = Qualification.objects.all()

class QualificationCreateView(ObjectCreateView):
    """
    Класс для создания новой квалификации.
    """
    model = Qualification
    form_class = QualificationForm


#
## Group
#

class GroupTableView(ObjectTableView):
    """
    Класс для отображения таблицы групп.
    """
    table_class = GroupTable
    filterset_class = GroupFilter
    queryset = GroupStudents.objects.all()

class GroupDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации о группе.
    """
    paginate_by  = 30
    model= GroupStudents
    template_name = 'Contingent/detail/group_detail.html'

    fieldset = {
        'Основная информация':
            ['number', 'qualification']
    }

    def get_tables(self):
        students = Student.objects.filter(group__pk=self.object.pk)
        table = StudentTable2(data=students)

        gradebooks = Gradebook.objects.filter(group__pk=self.object.pk)
        table2 = GradebookTable2(data=gradebooks)

        table3 = DisciplineTable(data=self.object.disciplines.all())

        return [table, table2, table3]

class GroupUpdateView(ObjectUpdateView):
    """
    Класс для обновления информации о группе.
    """
    form_class = GroupForm
    queryset = GroupStudents.objects.all()

class GroupCreateView(ObjectCreateView):
    """
    Класс для создания новой группы.
    """
    model = GroupStudents
    form_class = GroupForm

#
## Student
#

class StudentTableView(ObjectTableView):
    """
    Класс для отображения таблицы студентов.
    """
    table_class = StudentTable
    filterset_class = StudentFilter
    queryset = Student.objects.all()

class StudentDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации о студенте.
    """
    model= Student
    paginate_by  = 30
    template_name = 'Contingent/detail/student_detail.html'

    fieldset = {
        'Основная информация':
            ['full_name', 'phone', 'birth_date', 'snils', 'course', 'group', 'admission_order', 'note'],
            
        'Образование':
            ['education_base', 'education_basis', 'transfer_to_2nd_year_order', 'transfer_to_3rd_year_order', 'transfer_to_4th_year_order', 'expelled_due_to_graduation', 'left_course'],
        
        'Контакты':
            ['registration_address', 'actual_address', 'representative_full_name', 'representative_email'],
    }


class StudentUpdateView(ObjectUpdateView):
    """
    Класс для обновления информации о студенте.
    """
    form_class = StudentForm
    queryset = Student.objects.all()

class StudentCreateView(ObjectCreateView):
    """
    Класс для создания нового студента.
    """
    model = Student
    form_class = StudentForm