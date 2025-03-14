import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django_tables2 import SingleTableMixin, RequestConfig
from django_filters.views import FilterView
from xhtml2pdf import pisa

from Curriculum.base.generic import ObjectCreateView, ObjectUpdateView, ObjectDetailView, ObjectListView, \
    ObjectTemplateView
from Curriculum.models import Discipline, Qualification, Specialty, GroupStudents, Student, RecordBookTemplate, \
    StudentRecordBook, ContingentMovement
from Curriculum.Сontingent.filters import *
from Curriculum.Сontingent.forms import *
from Curriculum.Сontingent.tables import *


class DisciplineTableView(ObjectTableView):
    """
    Представление для отображения таблицы дисциплин.
    """
    model = Discipline
    template_name = 'Contingent/discipline_list.html'
    table_class = DisciplineTable
    filterset_class = DisciplineFilter


class DisciplineDetailView(ObjectDetailView):
    """
    Представление для отображения детальной информации о дисциплине.
    """
    model = Discipline
    template_name = 'Contingent/detail/discipline_detail.html'


class DisciplineUpdateView(ObjectUpdateView):
    """
    Представление для обновления дисциплины.
    """
    model = Discipline
    form_class = DisciplineForm
    template_name = 'Contingent/update/discipline_form.html'


class DisciplineCreateView(ObjectCreateView):
    """
    Представление для создания дисциплины.
    """
    model = Discipline
    form_class = DisciplineForm
    template_name = 'Contingent/create/discipline_form.html'


class SpecialtyTableView(ObjectTableView):
    """
    Представление для отображения таблицы специальностей.
    """
    model = Specialty
    template_name = 'Contingent/specialty_list.html'
    table_class = SpecialtyTable
    filterset_class = SpecialtyFilter


class SpecialtyDetailView(ObjectDetailView):
    """
    Представление для отображения детальной информации о специальности.
    """
    model = Specialty
    template_name = 'Contingent/detail/specialty_detail.html'


class SpecialtyUpdateView(ObjectUpdateView):
    """
    Представление для обновления специальности.
    """
    model = Specialty
    form_class = SpecialtyForm
    template_name = 'Contingent/update/specialty_form.html'


class SpecialtyCreateView(ObjectCreateView):
    """
    Представление для создания специальности.
    """
    model = Specialty
    form_class = SpecialtyForm
    template_name = 'Contingent/create/specialty_form.html'


class QualificationTableView(ObjectTableView):
    """
    Представление для отображения таблицы квалификаций.
    """
    model = Qualification
    template_name = 'Contingent/qualification_list.html'
    table_class = QualificationTable
    filterset_class = QualificationFilter


class QualificationTableView(ObjectTableView):
    """
    Представление для отображения таблицы квалификаций.
    """
    model = Qualification
    template_name = 'Contingent/qualification_list.html'
    table_class = QualificationTable
    filterset_class = QualificationFilter


class QualificationDetailView(ObjectDetailView):
    """
    Представление для отображения детальной информации о квалификации.
    """
    model = Qualification
    template_name = 'Contingent/detail/qualification_detail.html'


class QualificationUpdateView(ObjectUpdateView):
    """
    Представление для обновления квалификации.
    """
    model = Qualification
    form_class = QualificationForm
    template_name = 'Contingent/update/qualification_form.html'


class QualificationCreateView(ObjectCreateView):
    """
    Представление для создания квалификации.
    """
    model = Qualification
    form_class = QualificationForm
    template_name = 'Contingent/create/qualification_form.html'


class GroupTableView(ObjectTableView):
    """
    Представление для отображения таблицы групп.
    """
    model = GroupStudents
    template_name = 'Contingent/group_list.html'
    table_class = GroupTable
    filterset_class = GroupFilter


class GroupDetailView(ObjectDetailView):
    """
    Представление для отображения детальной информации о группе.
    """
    model = GroupStudents
    template_name = 'Contingent/detail/group_detail.html'


class GroupUpdateView(ObjectUpdateView):
    """
    Представление для обновления группы.
    """
    model = GroupStudents
    form_class = GroupForm
    template_name = 'Contingent/update/group_form.html'


class GroupCreateView(ObjectCreateView):
    """
    Представление для создания группы.
    """
    model = GroupStudents
    form_class = GroupForm
    template_name = 'Contingent/create/group_form.html'


class StudentTableView(ObjectTableView):
    """
    Представление для отображения таблицы студентов.
    """
    model = Student
    template_name = 'Contingent/student_list.html'
    table_class = StudentTable
    filterset_class = StudentFilter


class StudentDetailView(ObjectDetailView):
    """
    Представление для отображения детальной информации о студенте.
    """
    model = Student
    template_name = 'Contingent/detail/student_detail.html'


class StudentUpdateView(ObjectUpdateView):
    """
    Представление для обновления студента.
    """
    model = Student
    form_class = StudentForm
    template_name = 'Contingent/update/student_form.html'


class StudentCreateView(ObjectCreateView):
    """
    Представление для создания студента.
    """
    model = Student
    form_class = StudentForm
    template_name = 'Contingent/create/student_form.html'


class AcademUpdateView(ObjectUpdateView):
    """
    Представление для обновления академического отпуска
    """
    model = ContingentMovement
    form_class = AcademLeaveForm
    template_name = 'Contingent/academ_leave_form.html'


class AcademListView(ObjectTableView):
    """
    Представление для отображения таблицы академических отпусков
    """
    model = Student
    template_name = 'Contingent/academ_list.html'
    table_class = AcademTable
    filterset_class = AcademFilter

    def get_queryset(self):
        return Student.objects.filter(contingentmovement__movement_type='academ_leave')


class AcademReturn(ObjectUpdateView):
    """
    Представление для возвращения из академического отпуска
    """
    model = ContingentMovement
    form_class = AcademReturnForm
    template_name = 'Contingent/academ_leave_form.html'


class ExpulsionListView(ObjectTableView):
    """
    Представление для отображения таблицы отчисленных студентов
    """
    model = Student
    template_name = 'Contingent/expulsion_list.html'
    table_class = ExpulsionTable
    filterset_class = ExpulsionFilter

    def get_queryset(self):
        return Student.objects.filter(contingentmovement__movement_type='expelled')


class ExpelStudent(ObjectUpdateView):
    """
    Представление для отчисления студента
    """
    model = ContingentMovement
    form_class = ExpellStudentForm
    template_name = 'Contingent/expulsion_form.html'


class RecoverStudent(ObjectUpdateView):
    """
    Представление для восстановления студента
    """
    model = ContingentMovement
    form_class = RecoverStudentForm
    template_name = 'Contingent/expulsion_form.html'


class StatisticksView(ObjectTemplateView):
    """
    Представление для отображения статистики
    """
    template_name = 'Contingent/statisticks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = generate_statistics_table(self.request)
        context['group_table'] = generate_group_table(self.request)
        context['course_table'] = generate_course_table(self.request, self.request.GET.get('course', 1))
        context['vacation_table'] = generate_vacation_table(self.request)
        context['movement_table'] = generate_movement_table(self.request)
        return context


def student_format_to_list():
    students = Student.objects.all()
    data = []
    for student in students:
        data.append({
            'id': student.id,
            'last_name': student.last_name,
            'first_name': student.first_name,
            'middle_name': student.middle_name,
            'birth_date': student.birth_date,
            'group': student.group.name,
        })
    return data


def qualification_detail(request, qualification_id):
    # получите квалификацию по идентификатору
    qualification = get_object_or_404(Qualification, pk=qualification_id)
    # получите список годов поступления для этой квалификации (предположим, что у вас есть поле admission_year в модели Group)
    admission_years = GroupStudents.objects.filter(qualification=qualification).values_list('admission_year',
                                                                                            flat=True).distinct()
    # передайте квалификацию и годы поступления в контекст шаблона
    context = {
        'qualification': qualification,
        'admission_years': admission_years,
    }
    return render(request, 'contingent/qualification_detail.html', context)


def save_record_book_template(request, qualification_id, admission_year):
    # получите квалификацию по идентификатору
    qualification = get_object_or_404(Qualification, pk=qualification_id)
    # получите группу по квалификации и году поступления (предположим, что у вас есть модель Group)
    group = get_object_or_404(GroupStudents, qualification=qualification, admission_year=admission_year)
    # получите учебный план для этой группы (предположим, что у вас есть поле curriculum в модели Group)
    curriculum = group.curriculum
    # получите элементы учебного плана (предположим, что у вас есть модель CurriculumItem и ManyToManyField items в модели Curriculum)
    curriculum_items = curriculum.items.all()
    # создайте шаблон зачетной книжки (предположим, что у вас есть модель RecordBookTemplate)
    record_book_template = RecordBookTemplate.objects.create(
        qualification=qualification,
        admission_year=admission_year,
    )
    # добавьте элементы учебного плана в шаблон зачетной книжки (предположим, что у вас есть ManyToManyField items в модели RecordBookTemplate)
    record_book_template.items.add(*curriculum_items)
    # перенаправьте пользователя на страницу детального просмотра шаблона зачетной книжки
    return redirect('record_book_template_detail', pk=record_book_template.pk)


class ViewRecordBookTemplateView(ObjectTemplateView):
    """
    Представление для просмотра шаблона зачетной книжки
    """
    template_name = 'Contingent/record_book_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qualification_id = self.kwargs.get('qualification_id')
        qualification = get_object_or_404(Qualification, pk=qualification_id)
        context['qualification'] = qualification
        context['groups'] = GroupStudents.objects.filter(specialty__qualification=qualification)
        return context


class ViewRecordBookView(ObjectTemplateView):
    """
    Представление для просмотра зачетной книжки студента
    """
    template_name = 'Contingent/record_book_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs.get('pk')
        student = get_object_or_404(Student, pk=student_id)
        context['student'] = student
        context['record_book'] = StudentRecordBook.objects.get(student=student)
        return context


class EditRecordBookTemplateView(ObjectUpdateView):
    """
    Представление для редактирования шаблона зачетной книжки
    """
    model = RecordBookTemplate
    fields = '__all__'
    template_name = 'Contingent/record_book_edit.html'

    def get_object(self, queryset=None):
        qualification_id = self.kwargs.get('qualification_id')
        admission_year = self.kwargs.get('admission_year')
        obj, created = RecordBookTemplate.objects.get_or_create(
            qualification_id=qualification_id,
            admission_year=admission_year
        )
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qualification'] = get_object_or_404(Qualification, pk=self.kwargs.get('qualification_id'))
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Шаблон зачетной книжки успешно сохранен')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('contingent:view_record_book_template',
                            kwargs={'qualification_id': self.kwargs.get('qualification_id')})


def generate_student_record_book(request, pk):
    student = get_object_or_404(Student, pk=pk)
    group = student.group
    qualification = group.specialty.qualification
    admission_year = group.year
    record_book_template = get_object_or_404(RecordBookTemplate, qualification=qualification,
                                            admission_year=admission_year)
    student_record_book = StudentRecordBook.objects.create(student=student, record_book_template=record_book_template)
    return redirect('student_detail', pk=pk)


def create_auto_record_book_template(request, qualification_id, admission_year):
    qualification = get_object_or_404(Qualification, pk=qualification_id)
    record_book_template = RecordBookTemplate.objects.create(qualification=qualification,
                                                            admission_year=admission_year)
    return redirect('qualification_detail', qualification_id=qualification_id)


def generate_group_recordbooks(request, group_id):
    group = get_object_or_404(GroupStudents, pk=group_id)
    students = group.student_set.all()
    qualification = group.specialty.qualification
    admission_year = group.year
    record_book_template, created = RecordBookTemplate.objects.get_or_create(qualification=qualification,
                                                                              admission_year=admission_year)

    for student in students:
        StudentRecordBook.objects.get_or_create(student=student, record_book_template=record_book_template)

    return redirect('group_detail', pk=group_id)


def generate_unique_record_book_number(admission_year):
    # Получаем текущий год
    current_year = datetime.datetime.now().year

    # Получаем количество записей с таким же годом поступления
    count = Student.objects.filter(group__year=admission_year).count()

    # Формируем уникальный номер
    unique_number = f"{current_year}-{count + 1}"

    return unique_number


class ContingentMovementTableView(SingleTableMixin, FilterView):
    """
    Представление для отображения таблицы движения контингента студентов.
    """
    table_class = ContingentMovementTable
    model = ContingentMovement
    template_name = 'Contingent/contingent_movement_list.html'
    filterset_class = ContingentMovementFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Движение контингента студентов'
        return context


def generate_group_table(request):
    groups = GroupStudents.objects.all()
    table_data = [{'group': group, 'count': group.student_set.count()} for group in groups]
    table = StatisticksTable(table_data)
    RequestConfig(request).configure(table)
    return table


def generate_course_table(request, course):
    students = Student.objects.filter(group__course_number=course)
    table_data = [{'group': student.group, 'count': 1} for student in students]
    table = StatisticksTable(table_data)
    RequestConfig(request).configure(table)
    return table


def generate_statistics_table(request):
    # Получите данные из вашей модели
    students = Student.objects.all()

    # Создайте данные для таблицы
    table_data = [
        {'group': student.group, 'count': 1, 'type': student.status}
        for student in students
    ]

    # Создайте таблицу
    table = StatisticksTable(table_data)
    RequestConfig(request).configure(table)
    return table


def generate_vacation_table(request):
    students = Student.objects.filter(status='academ')
    table_data = [{'group': student.group, 'count': 1} for student in students]
    table = StatisticksTable(table_data)
    RequestConfig(request).configure(table)
    return table


def generate_movement_table(request):
    students = Student.objects.all()

    # Создайте данные для таблицы
    table_data = [
        {'group': student.group, 'count': 1, 'type': student.status}
        for student in students
    ]

    # Создайте таблицу
    table = StatisticksTable(table_data)
    RequestConfig(request).configure(table)
    return table


def import_students(request):
    if request.method == 'POST':
        form = StudentImportForm(request.POST, request.FILES)
        if form.is_valid():
            # students = form.cleaned_data['students']
            # for student_data in students:
            #     Student.objects.create(**student_data)
            messages.add_message(request, messages.SUCCESS, 'Студенты успешно импортированы')
            return redirect('student_list')
    else:
        form = StudentImportForm()
    return render(request, 'Contingent/import_students.html', {'form': form})