from .forms import *
from .tables import *
from .filters import *
from Academhub.models import GroupStudents, Qualification, Specialty, Student
from Academhub.base import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView


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

    def get_table(self):
        students = Qualification.objects.filter(specialty__pk=self.object.pk)
        table = QualificationTable(data=students)
        return table

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

    def get_table(self):
        students = GroupStudents.objects.filter(qualification__pk=self.object.pk)
        table = GroupTable(data=students)
        return table

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

    def get_table(self):
        students = Student.objects.filter(group__pk=self.object.pk)
        table = StudentTable2(data=students)
        return table

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


