from contextlib import nullcontext

from django.views import View

from .filters import AcademFilter
from .forms import *
from .forms import AcademLeaveForm, AcademReturnForm
from .tables import *
from .filters import *
from Academhub.models import (
    Student, 
    Practice,
    TermPaper,
    Specialty, 
    Gradebook, 
    Discipline, 
    Curriculum, 
    GroupStudents, 
    Qualification,
    RecordBookTemplate, 
    ProfessionalModule,
    MiddleCertification,
)
from Gradebook.tables import GradebookTable2
from django.shortcuts import render, get_object_or_404, redirect
from Academhub.base import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView

__all__ = (
    'view_record_book',
    'save_record_book_template',
    'create_record_book_template',

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

from .tables import AcademTable


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

#
##
#

class AcademUpdateView(ObjectUpdateView):
    """
    Класс для отправки студента в академ.
    """
    form_class = AcademLeaveForm
    queryset = Student.objects.all()

class AcademListView(ObjectTableView):
    """
    Класс для просмотра студентов, находящихся в академе
    """
    table_class = AcademTable
    filterset_class = AcademFilter
    queryset = Student.objects.filter(is_in_academ=True)
    template_name = 'Contingent/academ_list.html'

class AcademReturn(ObjectUpdateView):
    form_class = AcademReturnForm
    queryset = Student.objects.all()



def qualification_detail(request, qualification_id):
    qualification = get_object_or_404(Qualification, id=qualification_id)
    # Предположим, что admission_year выбирается пользователем или берется текущий год
    admission_year = 2023  # Замените на логику выбора года
    return render(request, 'qualification_detail.html',
                  {'qualification': qualification, 'admission_year': admission_year})


def create_record_book_template(request, qualification_id, admission_year):
    qualification = get_object_or_404(Qualification, id=qualification_id)
    curriculum = get_object_or_404(Curriculum, qualification=qualification, admission_year=admission_year)
    template, created = RecordBookTemplate.objects.get_or_create(qualification=qualification,
                                                                 admission_year=admission_year, curriculum=curriculum)

    curriculum_disciplines = [{"id": d.id, "name": d.name} for d in curriculum.disciplines.all()]

    return render(request, 'Contingent/record_book_template.html', {
        'qualification': qualification,
        'template': template,
        'curriculum': curriculum,
        'curriculum_disciplines': curriculum_disciplines,
        'admission_year': admission_year,
    })


def save_record_book_template(request, qualification_id, admission_year):
    qualification = get_object_or_404(Qualification, id=qualification_id)
    curriculum = get_object_or_404(Curriculum, qualification=qualification, admission_year=admission_year)
    template = RecordBookTemplate.objects.get(qualification=qualification, admission_year=admission_year)

    if request.method == 'POST':
        # Обновление основной информации
        template.student_name = request.POST.get('student_name', '')
        template.record_book_number = request.POST.get('record_book_number', '')
        template.admission_order = request.POST.get('admission_order', '')
        template.issue_date = request.POST.get('issue_date')
        template.save()

        # Обработка промежуточных аттестаций
        middle_semesters = request.POST.getlist('middle_semester[]')
        middle_disciplines = request.POST.getlist('middle_discipline[]')
        middle_hours = request.POST.getlist('middle_hours[]')
        middle_is_exams = request.POST.getlist('middle_is_exam[]')
        template.middle_certifications.clear()
        for sem, disc, hrs, is_exam in zip(middle_semesters, middle_disciplines, middle_hours, middle_is_exams):
            cert = MiddleCertification.objects.create(
                semester=sem,
                discipline_id=disc,
                hours=hrs,
                is_exam=is_exam == 'True'
            )
            template.middle_certifications.add(cert)

        # Обработка модулей
        module_names = request.POST.getlist('module_name[]')
        module_hours = request.POST.getlist('module_hours[]')
        template.professional_modules.clear()
        for name, hrs in zip(module_names, module_hours):
            module = ProfessionalModule.objects.create(module_name=name, hours=hrs)
            template.professional_modules.add(module)

        # Обработка практик
        practice_names = request.POST.getlist('practice_name[]')
        practice_hours = request.POST.getlist('practice_hours[]')
        practice_semesters = request.POST.getlist('practice_semester[]')
        template.practices.clear()
        for name, hrs, sem in zip(practice_names, practice_hours, practice_semesters):
            practice = Practice.objects.create(practice_name=name, hours=hrs, semester=sem, practice_type='УП')
            template.practices.add(practice)

        # Обработка курсовых
        term_disciplines = request.POST.getlist('term_discipline[]')
        term_topics = request.POST.getlist('term_topic[]')
        term_grades = request.POST.getlist('term_grade[]')
        template.term_papers.clear()
        for disc, topic, grade in zip(term_disciplines, term_topics, term_grades):
            paper = TermPaper.objects.create(discipline_id=disc, topic=topic, grade=grade)
            template.term_papers.add(paper)

        # return redirect('qualification_detail', pk=qualification_id)
        return redirect('view_record_book', qualification_id=qualification_id, admission_year=admission_year)

    return redirect('create_record_book_template', qualification_id=qualification_id, admission_year=admission_year)


def view_record_book(request, qualification_id, admission_year):
    qualification = get_object_or_404(Qualification, id=qualification_id)
    template = get_object_or_404(RecordBookTemplate, qualification=qualification, admission_year=admission_year)

    context = {
        'qualification': qualification,
        'template': template,
        'admission_year': admission_year,
    }
    return render(request, 'Contingent/record_book_view.html', context)

