from collections import defaultdict
from contextlib import nullcontext

from django.views import View

from .filters import AcademFilter, ExpulsionFilter
from .forms import *
from .forms import AcademLeaveForm, AcademReturnForm, ExpellStudentForm, RecoverStudentForm
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
from Academhub.base import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView, ObjectListView, \
    Navigation

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

from .tables import AcademTable, ExpulsionTable


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
        students = Student.objects.filter(group__pk=self.object.pk, is_expelled=False, is_in_academ=False)
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
    queryset = Student.objects.filter(is_expelled=False, is_in_academ=False)

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


class ExpulsionListView(ObjectTableView):
    table_class = ExpulsionTable
    filterset_class = ExpulsionFilter
    queryset = Student.objects.filter(is_expelled=True)

class ExpelStudent(ObjectUpdateView):
    form_class = ExpellStudentForm
    queryset = Student.objects.all()

class RecoverStudent(ObjectUpdateView):
    form_class = RecoverStudentForm
    queryset = Student.objects.filter(is_expelled=True)

# class StatisticksView(ObjectListView):
#     template_name = 'Contingent/statisticks.html'


def student_format_to_list():
    students = []
    for student in Student.objects.all():
        student_specialty = student.group.qualification.specialty
        student_qualification = student.group.qualification.name
        student_current_course = student.group.current_course
        student_education_base = student.education_base
        student_education_basis = student.education_basis
        student_is_in_academ = student.is_in_academ

        students.append({"specialty_code": student_specialty.code, "specialty_name": student_specialty.name,
                         "qualification": student_qualification,
                         "course": student_current_course, "base": student_education_base, "budget": student_education_basis,
                         "academic_leave": student_is_in_academ})
    return students
def statisticks_view(request):
    student_list = student_format_to_list()

    specialty_data = defaultdict(lambda: defaultdict(int))
    all_specialties = list(Specialty.objects.all().values_list())
    print(all_specialties)

    # Инициализируем все направления заранее
    for qualification in Qualification.objects.all():
        specialty_data[(qualification.specialty.code, qualification.specialty.name, qualification.name)]  # Создаем пустые записи
        all_specialties = [spec for spec in all_specialties if spec[0] != qualification.specialty.id]

    for specialty in all_specialties:
        specialty_data[(specialty[1], specialty[2], "")]


    for student in student_list:
        spec_code = student["specialty_code"]
        spec_name = student["specialty_name"]
        qualification = student["qualification"]
        course = student["course"]
        base = student["base"]  # Основное общее или Среднее общее
        budget = student["budget"]  # Бюджет или Внебюджет
        academic = student["academic_leave"]  # True - в академе, False - нет

        if base == "Основное общее":
            base = 9
        else:
            base = 11

        if academic:
            key = f"students_academic_{course}_{'budget' if budget else 'paid'}"
        else:
            key = f"students_{base}_{course}_{'budget' if budget else 'paid'}"

        specialty_data[(spec_code, spec_name, qualification)][key] += 1

    number = 1
    table_data = []
    total_9_1_ = 0
    total_9_2_ = 0
    total_9_3_ = 0
    total_9_4_ = 0

    total_11_1_ = 0
    total_11_2_ = 0
    total_11_3_ = 0

    total_academ_1 = 0
    total_academ_2 = 0
    total_academ_3 = 0
    total_academ_4 = 0

    total_contingent = 0

    for (code, name, qualification), counts in specialty_data.items():
        total_budget = sum(counts.get(key, 0) for key in counts if "budget" in key)
        total_paid = sum(counts.get(key, 0) for key in counts if "paid" in key)

        total_9_1_ += sum(counts.get(key, 0) for key in counts if "9_1" in key)
        total_9_2_ += sum(counts.get(key, 0) for key in counts if "9_2" in key)
        total_9_3_ += sum(counts.get(key, 0) for key in counts if "9_3" in key)
        total_9_4_ += sum(counts.get(key, 0) for key in counts if "9_4" in key)

        total_11_1_ += sum(counts.get(key, 0) for key in counts if "11_1" in key)
        total_11_2_ += sum(counts.get(key, 0) for key in counts if "11_2" in key)
        total_11_3_ += sum(counts.get(key, 0) for key in counts if "11_3" in key)

        total_academ_1 += sum(counts.get(key, 0) for key in counts if "academic_1" in key)
        total_academ_2 += sum(counts.get(key, 0) for key in counts if "academic_2" in key)
        total_academ_3 += sum(counts.get(key, 0) for key in counts if "academic_3" in key)
        total_academ_4 += sum(counts.get(key, 0) for key in counts if "academic_4" in key)

        total_contingent += total_budget + total_paid

        row = [
            number,
            code,  # Код специальности
            name,  # Название специальности
            qualification,  # Квалификация
            counts.get("students_9_1_budget", 0),
            counts.get("students_9_1_paid", 0),
            counts.get("students_9_2_budget", 0),
            counts.get("students_9_2_paid", 0),
            counts.get("students_9_3_budget", 0),
            counts.get("students_9_3_paid", 0),
            counts.get("students_9_4_budget", 0),
            counts.get("students_9_4_paid", 0),
            counts.get("students_11_1_budget", 0),
            counts.get("students_11_1_paid", 0),
            counts.get("students_11_2_budget", 0),
            counts.get("students_11_2_paid", 0),
            counts.get("students_11_3_budget", 0),
            counts.get("students_11_3_paid", 0),
            counts.get("students_academic_1_budget", 0),
            counts.get("students_academic_1_paid", 0),
            counts.get("students_academic_2_budget", 0),
            counts.get("students_academic_2_paid", 0),
            counts.get("students_academic_3_budget", 0),
            counts.get("students_academic_3_paid", 0),
            counts.get("students_academic_4_budget", 0),
            counts.get("students_academic_4_paid", 0),
            total_budget,  # Итого бюджет
            total_paid,  # Итого внебюджет
        ]
        table_data.append(row)
        number += 1

    last_row = [total_9_1_, total_9_2_, total_9_3_, total_9_4_, total_11_1_, total_11_2_, total_11_3_, total_academ_1,
                total_academ_2, total_academ_3, total_academ_4, total_contingent]

    total_09_02_07_budget = sum(
        counts.get(key, 0)
        for (code, _, _), counts in specialty_data.items()
        if code == "09.02.07"
        for key in counts
        if "budget" in key and not key.startswith("students_9_1")
    )

    total_09_02_07_paid = sum(
        counts.get(key, 0)
        for (code, _, _), counts in specialty_data.items()
        if code == "09.02.07"
        for key in counts
        if "paid" in key and not key.startswith("students_9_1")
    )

    return render(request, 'Contingent/statisticks.html', context={'table_data': table_data, 'last_row': last_row, 'total_09_02_07_budget': total_09_02_07_budget,
                                                                   'total_09_02_07_paid': total_09_02_07_paid})


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

