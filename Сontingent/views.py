from .forms import *
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
    StudentRecordBook,
    RecordBookTemplate,
    ProfessionalModule,
    MiddleCertification,
)
import random
import string
from Gradebook.tables import GradebookTable2
from django.shortcuts import render, get_object_or_404, redirect
from Academhub.base import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView, ObjectTemplateView

__all__ = (
    # 'view_record_book',
    'ViewRecordBookView',
    'ViewRecordBookTemplateView',
    'save_record_book_template',
    # 'create_record_book_template',
    'CreateRecordBookTemplateView',
    'EditRecordBookTemplateView',
    'GenerateRecordBookView',
    'generate_group_recordbooks',

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

        # table3 = DisciplineTable(data=self.object.disciplines.all())

        return [table, table2]

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

def qualification_detail(request, qualification_id):
    qualification = get_object_or_404(Qualification, id=qualification_id)
    # Предположим, что admission_year выбирается пользователем или берется текущий год
    admission_year = 2023  # Замените на логику выбора года
    return render(request, 'qualification_detail.html',
                  {'qualification': qualification, 'admission_year': admission_year})



from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


class CreateRecordBookTemplateView(CreateView):
    """
    Класс для ослздания ШАБОНА зачетной книжки.
    """
    model = RecordBookTemplate
    template_name = 'Contingent/record_book_template.html'
    fields = ['student_name', 'record_book_number', 'admission_order', 'issue_date']

    def get(self, request, *args, **kwargs):
        qualification = get_object_or_404(Qualification, id=self.kwargs['qualification_id'])
        try:
            RecordBookTemplate.objects.get(
                qualification=qualification,
                admission_year=self.kwargs['admission_year']
            )
            return redirect('view_record_book', qualification_id=self.kwargs['qualification_id'],
                            admission_year=self.kwargs['admission_year'])
        except RecordBookTemplate.DoesNotExist:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qualification = get_object_or_404(Qualification, id=self.kwargs['qualification_id'])
        curriculum = get_object_or_404(Curriculum, qualification=qualification,
                                       admission_year=self.kwargs['admission_year'])

        context['qualification'] = qualification
        context['admission_year'] = self.kwargs['admission_year']
        context['curriculum'] = curriculum
        context['curriculum_disciplines'] = [{"id": d.id, "name": d.name} for d in curriculum.disciplines.all()]
        context['url_list'] = 'qualification_list'
        context['model_verbose_name'] = 'Зачетная книжка'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.qualification = get_object_or_404(Qualification, id=self.kwargs['qualification_id'])
        self.object.admission_year = self.kwargs['admission_year']
        self.object.curriculum = get_object_or_404(Curriculum, qualification=self.object.qualification,
                                                   admission_year=self.kwargs['admission_year'])
        self.object.save()

        # Обработка промежуточных аттестаций
        middle_semesters = self.request.POST.getlist('middle_semester[]')
        middle_disciplines = self.request.POST.getlist('middle_discipline[]')
        middle_hours = self.request.POST.getlist('middle_hours[]')
        middle_is_exams = self.request.POST.getlist('middle_is_exam[]')
        self.object.middle_certifications.clear()
        for sem, disc, hrs, is_exam in zip(middle_semesters, middle_disciplines, middle_hours, middle_is_exams):
            cert = MiddleCertification.objects.create(
                semester=sem,
                discipline_id=disc,
                hours=hrs,
                is_exam=is_exam == 'True'
            )
            self.object.middle_certifications.add(cert)

        # Обработка модулей
        module_names = self.request.POST.getlist('module_name[]')
        module_hours = self.request.POST.getlist('module_hours[]')
        self.object.professional_modules.clear()
        for name, hrs in zip(module_names, module_hours):
            module = ProfessionalModule.objects.create(module_name=name, hours=hrs)
            self.object.professional_modules.add(module)

        # Обработка практик
        practice_names = self.request.POST.getlist('practice_name[]')
        practice_hours = self.request.POST.getlist('practice_hours[]')
        practice_semesters = self.request.POST.getlist('practice_semester[]')
        self.object.practices.clear()
        for name, hrs, sem in zip(practice_names, practice_hours, practice_semesters):
            practice = Practice.objects.create(practice_name=name, hours=hrs, semester=sem, practice_type='УП')
            self.object.practices.add(practice)

        # Обработка курсовых (без topic и grade)
        term_disciplines = self.request.POST.getlist('term_discipline[]')
        self.object.term_papers.clear()
        for disc in term_disciplines:
            paper = TermPaper.objects.create(discipline_id=disc)
            self.object.term_papers.add(paper)

        return redirect('view_record_book', qualification_id=self.kwargs['qualification_id'],
                        admission_year=self.kwargs['admission_year'])

    def get_success_url(self):
        return reverse_lazy('view_record_book', kwargs={'qualification_id': self.kwargs['qualification_id'],
                                                        'admission_year': self.kwargs['admission_year']})


def save_record_book_template(request, qualification_id, admission_year):
    """
    Функция для сохранения ШАБЛОНА зачетной книжки
    """
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
        return redirect('view_record_book_template', qualification_id=qualification_id, admission_year=admission_year)

    return redirect('create_record_book_template', qualification_id=qualification_id, admission_year=admission_year)


class ViewRecordBookTemplateView(ObjectTemplateView):
    """
    Класс для отображения ШАБЛОНА зачетной книжки.
    """
    template_name = 'Contingent/record_book_view.html'
    model = RecordBookTemplate

    def get_context_data(self, **kwargs):
        # Получаем базовый контекст от родительских классов
        context = super().get_context_data(**kwargs)

        qualification = get_object_or_404(Qualification, id=self.kwargs['qualification_id'])
        template = get_object_or_404(RecordBookTemplate, qualification=qualification,
                                     admission_year=self.kwargs['admission_year'])

        context['qualification'] = qualification
        context['template'] = template
        context['admission_year'] = self.kwargs['admission_year']
        context['url_list'] = 'qualification_list'

        return context

class ViewRecordBookView(ObjectTemplateView):
    """
    Класс для отображения информации о зачетной книжке конкретного студента.
    """
    template_name = 'Contingent/record_book_view.html'
    model = StudentRecordBook

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qualification = get_object_or_404(Qualification, id=self.kwargs['qualification_id'])
        template = get_object_or_404(StudentRecordBook, student=self.kwargs['student_id'])
        context['qualification'] = qualification

        context['qualification'] = qualification
        context['template'] = template
        context['admission_year'] = self.kwargs['admission_year']
        context['url_list'] = 'student_list'
        context['is_student_gradebbok'] = True
        context['student_id'] = self.kwargs['student_id']
        return context

class EditRecordBookTemplateView(ObjectUpdateView):
    """
    редактирование Шаблоа зачетки студентов
    """
    model = RecordBookTemplate
    template_name = 'Contingent/record_book_edit.html'
    fields = ['student_name', 'record_book_number', 'admission_order', 'issue_date']

    def get_object(self, queryset=None):
        qualification = get_object_or_404(Qualification, id=self.kwargs['qualification_id'])
        return get_object_or_404(RecordBookTemplate, qualification=qualification, admission_year=self.kwargs['admission_year'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qualification = get_object_or_404(Qualification, id=self.kwargs['qualification_id'])
        context['qualification'] = qualification
        context['admission_year'] = self.kwargs['admission_year']
        context['curriculum'] = self.object.curriculum
        context['curriculum_disciplines'] = [{"id": d.id, "name": d.name} for d in self.object.curriculum.disciplines.all()]
        context['url_list'] = 'qualification_list'
        context['mobel_verbosename'] = self.get_verbose_name()  # Совместимость с ObjectUpdateView
        return context

    def form_valid(self, form):
        self.object = form.save()

        # Обработка дополнительных данных формы
        middle_semesters = self.request.POST.getlist('middle_semester[]')
        middle_disciplines = self.request.POST.getlist('middle_discipline[]')
        middle_hours = self.request.POST.getlist('middle_hours[]')
        middle_is_exams = self.request.POST.getlist('middle_is_exam[]')
        self.object.middle_certifications.clear()
        for sem, disc, hrs, is_exam in zip(middle_semesters, middle_disciplines, middle_hours, middle_is_exams):
            cert = MiddleCertification.objects.create(
                semester=sem,
                discipline_id=disc,
                hours=hrs,
                is_exam=is_exam == 'True'
            )
            self.object.middle_certifications.add(cert)

        module_names = self.request.POST.getlist('module_name[]')
        module_hours = self.request.POST.getlist('module_hours[]')
        self.object.professional_modules.clear()
        for name, hrs in zip(module_names, module_hours):
            module = ProfessionalModule.objects.create(module_name=name, hours=hrs)
            self.object.professional_modules.add(module)

        practice_names = self.request.POST.getlist('practice_name[]')
        practice_hours = self.request.POST.getlist('practice_hours[]')
        practice_semesters = self.request.POST.getlist('practice_semester[]')
        self.object.practices.clear()
        for name, hrs, sem in zip(practice_names, practice_hours, practice_semesters):
            practice = Practice.objects.create(practice_name=name, hours=hrs, semester=sem, practice_type='УП')
            self.object.practices.add(practice)

        term_disciplines = self.request.POST.getlist('term_discipline[]')
        self.object.term_papers.clear()
        for disc in term_disciplines:
            paper = TermPaper.objects.create(discipline_id=disc)
            self.object.term_papers.add(paper)

        return redirect('view_record_book', qualification_id=self.kwargs['qualification_id'], admission_year=self.kwargs['admission_year'])

    def get_success_url(self):
        return reverse_lazy('view_record_book_template', kwargs={'qualification_id': self.kwargs['qualification_id'], 'admission_year': self.kwargs['admission_year']})


def generate_unique_record_book_number(admission_year):
    """
    Генерирует уникальный номер зачётной книжки в формате Д1591Б/21/СПО.
    """
    while True:
        letters = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        prefix = random.choice(letters)
        suffix = random.choice(letters)
        number = ''.join(random.choices(string.digits, k=4))
        year_short = str(admission_year)[-2:]
        record_book_number = f"{prefix}{number}{suffix}/{year_short}/СПО"

        if not StudentRecordBook.objects.filter(record_book_number=record_book_number).exists():
            return record_book_number


class GenerateRecordBookView(ObjectDetailView):
    """
    Генерирует зачетные книжки для студента по шаблону для его специальности
    """
    def get(self, request, student_id):
        student = get_object_or_404(Student, id=student_id)
        qualification = student.group.qualification
        admission_year = student.group.year_create

        template = get_object_or_404(RecordBookTemplate, qualification=qualification, admission_year=admission_year)

        # Генерация уникального номера зачетки
        record_book_number = generate_unique_record_book_number(admission_year)

        # Создаём новый объект StudentRecordBook для студента
        new_record_book = StudentRecordBook.objects.create(
            student=student,
            qualification=qualification,
            admission_year=admission_year,
            student_name=f"{student.full_name}",
            record_book_number=record_book_number,
            admission_order=template.admission_order,
            issue_date=template.issue_date,
            curriculum=template.curriculum
        )

        # Копируем ManyToMany-поля из шаблона
        new_record_book.middle_certifications.set(template.middle_certifications.all())
        new_record_book.professional_modules.set(template.professional_modules.all())
        new_record_book.practices.set(template.practices.all())
        new_record_book.term_papers.set(template.term_papers.all())

        # Связываем зачётку со студентом
        student.record_book = new_record_book
        student.save()

        return redirect('view_record_book', qualification_id=qualification.id, admission_year=admission_year)




def generate_group_recordbooks(request, group_id):
    """
    Генерирует зачетки на всю группу
    """
    group = get_object_or_404(GroupStudents, id=group_id)
    qualification = group.qualification
    admission_year = group.year_create

    template = get_object_or_404(RecordBookTemplate, qualification=qualification, admission_year=admission_year)

    students = group.students.filter(record_book__isnull=True)
    for student in students:

        record_book_number = generate_unique_record_book_number(admission_year)

        new_record_book = StudentRecordBook.objects.create(
            student=student,
            qualification=qualification,
            admission_year=admission_year,
            student_name=f"{student.full_name}",
            record_book_number=record_book_number,
            admission_order=template.admission_order,
            issue_date=template.issue_date,
            curriculum=template.curriculum
        )

        # Копируем ManyToMany-поля из шаблона
        new_record_book.middle_certifications.set(template.middle_certifications.all())
        new_record_book.professional_modules.set(template.professional_modules.all())
        new_record_book.practices.set(template.practices.all())
        new_record_book.term_papers.set(template.term_papers.all())

        # Связываем зачётку со студентом
        student.record_book = new_record_book
        student.save()

    return redirect('groupstudents_detail', pk=group_id)

