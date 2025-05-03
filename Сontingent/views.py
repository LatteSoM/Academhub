import os
from collections import defaultdict
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from Academhub.generic import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView, ObjectTemplateView, \
    ObjectTableImportView, PermissionBaseMixin
from Academhub.models import (
    Student,
    Specialty,
    Discipline,
    Curriculum,
    AcademStudent,
    GroupStudents,
    Qualification,
    StudentRecordBook,
    ContingentMovement,
    RecordBookTemplate,
)
from Academhub.models import SubTable
from Academhub.modules.documentGenPars import StatisticsTableGenerator, CourseTableGenerator, GroupTableGenerator, \
    VacationTableGenerator, MovementTableGenerator
from Academhub.utils import getpermission, getpattern
from .filters import *
from .filters import AcademFilter, ExpulsionFilter, ContingentMovementFilter
from .forms import *
from .forms import AcademLeaveForm, AcademReturnForm, ExpellStudentForm, RecoverStudentForm
from .forms import ContingentStudentImportForm, GenerateQualificationTemplateForm
from .tables import *
from .tables import AcademTable, ExpulsionTable, ContingentMovementTable
from .utils import *

__all__ = (

    'ViewRecordBookView',
    'create_auto_record_book_template',
    'generate_student_record_book',
    'generate_group_recordbooks',
    'PromoteGroupStudentsView',

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
    'PromoteStudentsView',

    'GroupTableView', 
    'GroupDetailView', 
    'GroupUpdateView', 
    'GroupCreateView',

    'QualificationTableView',
    'QualificationCreateView',
    'QualificationDetailView',
    'QualificationUpdateView',

    'ExpulsionListView',
    'AcademListView',

    'GenerateQualificationTemplate',
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

    permission_required = getpermission('Contingent', 'view_discipline')

    buttons = [
        Button (
            id='add',
            name = 'Добавить',
            link_name = getpattern(Discipline, 'add'),
            permission = getpermission('Contingent', 'create_discipline')
        )
    ]

class DisciplineDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации о дисциплине.
    """
    model= Discipline
    paginate_by  = 30

    permission_required = getpermission('Contingent', 'view_discipline')

    fieldset = {
        'Основная информация':
            ['name', 'code', 'specialty',]
    }

    buttons = [
        Button (
            id='change',
            name = 'Обновить',
            link_params = ['pk'],
            link_name = getpattern(Discipline, 'change'),
            permission = getpermission('Contingent', 'update_discipline')
        ),
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Discipline, 'list'),
            permission = getpermission('Contingent', 'view_discipline')
        )
    ]
        
class DisciplineUpdateView(ObjectUpdateView):
    """
    Класс для обновления информации о дисциплине.
    """
    form_class = DisciplineForm
    queryset = Discipline.objects.all()

    permission_required = getpermission('Contingent', 'update_discipline')

    buttons = [
        Button (
            id='to_object',
            name = 'К объекту',
            link_params = ['pk'],
            link_name = getpattern(Discipline, 'detail'),
            permission = getpermission('Contingent', 'view_discipline')
        ),
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Discipline, 'list'),
            permission = getpermission('Contingent', 'view_discipline')
        )
    ]
    
class DisciplineCreateView(ObjectCreateView):
    """
    Класс для создания новой дисциплины.
    """
    model = Discipline
    form_class = DisciplineForm

    permission_required = getpermission('Contingent', 'create_discipline')

    buttons = [
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Discipline, 'list'),
            permission = getpermission('Contingent', 'view_discipline')
        )
    ]

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

    permission_required = getpermission('Contingent', 'view_specialty')

    buttons = [
        Button (
            id='add',
            name = 'Добавить',
            link_name = getpattern(Specialty, 'add'),
            permission = getpermission('Contingent', 'create_specialty')
        )
    ]


class SpecialtyDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации о специальности.
    """
    model= Specialty
    paginate_by  = 30
    template_name = 'Contingent/detail/specialty_detail.html'

    permission_required = getpermission('Contingent', 'view_specialty')

    fieldset = {
        'Основная информация':
            ['code', 'name'],
    }

    tables = [
        SubTable(
            name='Квалификации',
            filter_key='specialty',
            table=QualificationTable,
            queryset=Qualification.objects.all(),
        )
    ]

    buttons = [
        Button (
            id = 'change',
            name = 'Обновить',
            link_params = ['pk'],
            link_name = getpattern(Specialty, 'change'),
            permission = getpermission('Contingent', 'update_specialty'),
        ),
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Specialty, 'list'),
            permission = getpermission('Contingent', 'view_specialty')
        )
    ]

class SpecialtyUpdateView(ObjectUpdateView):
    """
    Класс для обновления информации о специальности.
    """
    form_class = SpecialtyForm
    queryset = Specialty.objects.all()

    permission_required = getpermission('Contingent', 'update_specialty')

    buttons = [
        Button (
            id='to_object',
            name = 'К объекту',
            link_params = ['pk'],
            link_name = getpattern(Specialty, 'detail'),
            permission = getpermission('Contingent', 'view_specialty')
        ),
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Specialty, 'list'),
            permission = getpermission('Contingent', 'view_specialty')
        )
    ]

class SpecialtyCreateView(ObjectCreateView):
    """
    Класс для создания новой специальности.
    """
    model = Specialty
    form_class = SpecialtyForm

    permission_required = getpermission('Contingent', 'create_specialty')

    buttons = [
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Specialty, 'list'),
            permission = getpermission('Contingent', 'view_specialty')
        )
    ]
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

    permission_required = getpermission('Contingent', 'view_qualification')

    buttons = [
        Button (
            id='add',
            name = 'Добавить',
            link_name = getpattern(Qualification, 'add'),
            permission = getpermission('Contingent', 'create_qualification'),
        )
    ]

class QualificationDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации о квалификации.
    """
    model= Qualification
    paginate_by  = 30
    template_name = 'Contingent/detail/qualification_detail.html'

    permission_required = getpermission('Contingent', 'view_qualification')

    fieldset = {
        'Основная информация':
            ['short_name', 'name', 'specialty']
    }

    buttons = [
        Button (
            id = 'change',
            name = 'Обновить',
            link_params = ['pk'],
            link_name = getpattern(Qualification, 'change'),
            permission = getpermission('Contingent', 'update_qualification'),
        ),
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Qualification, 'list'),
            permission = getpermission('Contingent', 'view_qualification')
        )
    ]

class QualificationUpdateView(ObjectUpdateView):
    """
    Класс для обновления информации о квалификации.
    """
    form_class = QualificationForm
    queryset = Qualification.objects.all()

    permission_required = getpermission('Contingent', 'update_qualification')

    buttons = [
        Button (
            id='to_object',
            name = 'К объекту',
            link_params = ['pk'],
            link_name = getpattern(Qualification, 'detail'),
            permission = getpermission('Contingent', 'view_qualification')
        ),
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Qualification, 'list'),
            permission = getpermission('Contingent', 'view_qualification')
        )
    ]

class QualificationCreateView(ObjectCreateView):
    """
    Класс для создания новой квалификации.
    """
    model = Qualification
    form_class = QualificationForm

    permission_required = getpermission('Contingent', 'create_qualification')

    buttons = [
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Qualification, 'list'),
            permission = getpermission('Contingent', 'view_qualification')
        )
    ]


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

    permission_required = getpermission('Contingent', 'view_group_student')

    buttons = [
        Button (
            id='add',
            name = 'Добавить',
            link_name = getpattern(GroupStudents, 'add'),
            permission = getpermission('Contingent', 'create_group_student'),
        )
    ]

    # create_template_recordbook_view(StudentRecordBook.objects.first())

class GroupDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации о группе.
    """
    paginate_by  = 30
    model= GroupStudents
    template_name = 'Contingent/detail/group_detail.html'

    permission_required = getpermission('Contingent', 'view_group_student')

    fieldset = {
        'Основная информация':[
            # 'number',
            'qualification'
        ]
    }

    tables = [
        SubTable (
            name='Студенты',
            filter_key='group',
            table=StudentTable2,
            queryset=CurrentStudent.objects.all(),
        ),
    ]

    buttons = [
        Button (
            id = 'change',
            name = 'Обновить',
            link_params = ['pk'],
            link_name = getpattern(GroupStudents, 'change'),
            permission = getpermission('Contingent', 'update_group_student'),
        ),
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(GroupStudents, 'list'),
            permission = getpermission('Contingent', 'view_group_student')
        )
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Подсчёт студентов
        student_count = self.object.students.count()  # Через связь Student
        try:
            current_student_count = CurrentStudent.objects.filter(group=self.object).count()
        except Exception as e:
            current_student_count = None
            print(f"Ошибка при подсчёте CurrentStudent: {e}")
        print(f"Количество студентов (CurrentStudent): {current_student_count}")
        context['student_count'] = student_count
        return context

class GroupUpdateView(ObjectUpdateView):
    """
    Класс для обновления информации о группе.
    """
    form_class = GroupForm
    queryset = GroupStudents.objects.all()

    permission_required = getpermission('Contingent', 'update_group_student')

    buttons = [
        Button (
            id='to_object',
            name = 'К объекту',
            link_params = ['pk'],
            link_name = getpattern(GroupStudents, 'detail'),
            permission = getpermission('Contingent', 'view_group_student')
        ),
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(GroupStudents, 'list'),
            permission = getpermission('Contingent', 'view_group_student')
        )
    ]


class PromoteGroupStudentsView(SuccessMessageMixin, ObjectUpdateView):
    """
    Перевод группы и всех студентов на следующий курс
    """
    model = GroupStudents
    form_class = PromoteGroupStudentsForm
    template_name = 'Contingent/promote_group_students_form.html'
    success_message = 'Группа и студенты были успешно переведены на следующий курс!'

    permission_required = getpermission('Contingent', 'transfer_students')

    def get_object(self, queryset=None):
        return get_object_or_404(GroupStudents, pk=self.kwargs['pk'])

    def form_valid(self, form):
        group = self.get_object()
        transfer_order = form.cleaned_data['transfer_order']
        success, message = transfer_group_students(group.pk, transfer_order)
        if success:
            return super().form_valid(form)
        else:
            form.add_error(None, message)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('groupstudents_detail', kwargs={'pk': self.get_object().pk})

class GroupCreateView(ObjectCreateView):
    """
    Класс для создания новой группы.
    """
    model = GroupStudents
    form_class = GroupForm

    permission_required = getpermission('Contingent', 'create_group_student')

    buttons = [
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(GroupStudents, 'list'),
            permission = getpermission('Contingent', 'view_group_student')
        )
    ]

#
## Student (живые)
#

class StudentTableView(ObjectTableImportView):
    """
    Класс для отображения таблицы студентов.
    """
    table_class = StudentTable
    filterset_class = StudentFilter
    form_import = ContingentStudentImportForm
    queryset = CurrentStudent.objects.all()

    permission_required = getpermission('Contingent', 'view_current_student')
    permission_import_required = getpermission('Contingent', 'export_student')

    buttons = [
        Button (
            id='add',
            name = 'Добавить',
            link_name = getpattern(Student, 'add'),
            permission = getpermission('Contingent', 'create_student'),
        ),
    ]


# class PromoteStudentsView(PermissionBaseMixin, FormView):
#     """
#     Класс для фильтрации и отображения студентов по параметрам.
#     """
#     model = CurrentStudent
#     form_class = PromoteStudentsForm
#     template_name = 'Contingent/transfer/transfer_students_form.html'
#
#     properties = ['education_base', 'education_basis', 'academic_debts', 'current_course']
#     success_url = reverse_lazy('transfer_students_form')
#
#     permission_required = getpermission('Contingent', 'transfer_students')
#
#     buttons = [
#         Button(
#             id='to_list',
#             name='К таблице',
#             link_name='transfer_students_list',
#         )
#     ]
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#
#         # Извлекаем параметры из URL
#         properties = {
#             'education_base': self.request.GET.get('education_base'),
#             'education_basis': self.request.GET.get('education_basis'),
#             'academic_debt': self.request.GET.get('academic_debts'),
#             'current_course': self.request.GET.get('current_course'),
#         }
#
#         # Передаем параметры в форму
#         kwargs['properties'] = properties
#         return kwargs
#
#     def get_form_kwargs(self):
#         """
#         Передаем параметры из URL в форму.
#         """
#         kwargs = super().get_form_kwargs()
#         kwargs['properties'] = self.request.GET.dict()
#         return kwargs
#
#     def form_valid(self, form):
#         """
#         Логика переводана студентов на следующий курс.
#         """
#         # Получаем список выбранных студентов
#         students = form.cleaned_data.get('students')
#         if not students:
#             form.add_error(None, "Вы не выбрали студентов для перевода.")
#             return self.form_invalid(form)
#
#         order_number = form.cleaned_data.get('order_number')
#
#         groups = set()
#
#         # Переводим студентов на следующий курс
#         for student in students:
#             try:
#                 groups.add(student.group)
#                 if student.group.current_course == 1:
#                     student.transfer_to_2nd_year_order = order_number
#                 elif student.group.current_course == 2:
#                     student.transfer_to_3rd_year_order = order_number
#                 elif student.group.current_course == 3:
#                     student.transfer_to_4th_year_order = order_number
#                 elif student.group.current_course == 4:
#                     student.expell_order = order_number
#                     student.is_expelled = True
#
#                 create_transfer_log(order_number, student)
#                 student.save()
#                 print('Зашли в валид')
#
#             except Exception as e:
#                 print(f"Ошибка при обработке студента {student.id}: {e}")
#                 continue
#
#             # print(type(student))
#             #
#             # create_transfer_log(order_number,student)
#             # student.save()
#
#
#         groups_qr = GroupStudents.objects.all()
#         for group in groups_qr:
#             if group in groups:
#
#                 # students.filter(group=group)
#                 current_students = CurrentStudent.objects.filter(group=group)
#
#                 current_course = group.current_course
#                 students_count = len(current_students)
#                 if current_course == 1:
#                     transfered_students = len(current_students.filter(transfer_to_2nd_year_order__isnull=False, transfer_to_3rd_year_order=None,
#                                                      transfer_to_4th_year_order=None))
#                     if students_count == transfered_students:
#                         group.current_course = 2
#                 if current_course == 2:
#                     transfered_students = len(
#                         current_students.filter(transfer_to_2nd_year_order__isnull=False, transfer_to_3rd_year_order__isnull=False,
#                                                      transfer_to_4th_year_order=None))
#                     if students_count == transfered_students:
#                         group.current_course = 3
#                 if current_course == 3:
#                     transfered_students = len(
#                         current_students.filter(transfer_to_2nd_year_order__isnull=False, transfer_to_3rd_year_order__isnull=False,
#                                                      transfer_to_4th_year_order__isnull=False))
#                     if students_count == transfered_students:
#                         group.current_course = 3
#
#                 # group.current_course += 1
#                 group.save()
#
#         return redirect(self.success_url)
#
#
#     def form_invalid(self, form):
#         """
#         Обработка ошибок формы.
#         """
#         return super().form_invalid(form)


#ЭТО РАБОТАЕТ
# from django.db import transaction
# from django.shortcuts import redirect
#
# class PromoteStudentsView(PermissionBaseMixin, FormView):
#     model = CurrentStudent
#     form_class = PromoteStudentsForm
#     template_name = 'Contingent/transfer/transfer_students_form.html'
#     success_url = reverse_lazy('transfer_students_form')
#     permission_required = getpermission('Contingent', 'transfer_students')
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['properties'] = self.request.GET.dict()
#         return kwargs
#
#     def form_valid(self, form):
#         students = form.cleaned_data.get('students')
#         if not students:
#             form.add_error(None, "Вы не выбрали студентов для перевода.")
#             return self.form_invalid(form)
#
#         order_number = form.cleaned_data.get('order_number')
#         groups = set()
#
#         print(f"Количество выбранных студентов: {len(students)}")
#         print(f"Номер приказа: {order_number}")
#
#         with transaction.atomic():
#             # Перевод студентов
#             for student in students:
#                 try:
#                     groups.add(student.group)
#                     print(f"Обрабатываем студента {student.id}, группа {student.group}, курс группы {student.group.current_course}")
#                     if student.group.current_course == 1:
#                         student.transfer_to_2nd_year_order = order_number
#                     elif student.group.current_course == 2:
#                         student.transfer_to_3rd_year_order = order_number
#                     elif student.group.current_course == 3:
#                         student.transfer_to_4th_year_order = order_number
#                     elif student.group.current_course == 4:
#                         student.expell_order = order_number
#                         student.is_expelled = True
#
#                     create_transfer_log(order_number, student)
#                     student.save()
#                     print(f"Студент {student.id} сохранён")
#                 except Exception as e:
#                     print(f"Ошибка при обработке студента {student.id}: {e}")
#                     continue
#
#             # Обновление курса групп
#             for group in groups:
#                 # Фильтруем только выбранных студентов в группе
#                 selected_students_in_group = [s for s in students if s.group == group]
#                 students_count = len(selected_students_in_group)
#                 current_course = group.current_course
#                 print(f"Группа {group.id}, курс {current_course}, выбрано студентов: {students_count}")
#
#                 if students_count == 0:
#                     print(f"Пропускаем группу {group.id}, так как нет выбранных студентов")
#                     continue
#
#                 if current_course == 1:
#                     transfered_students = len([s for s in selected_students_in_group if s.transfer_to_2nd_year_order == order_number])
#                     print(f"Переведено на 2-й курс: {transfered_students}")
#                     if students_count == transfered_students:
#                         group.current_course = 2
#                         group.save()
#                         print(f"Группа {group.id} переведена на 2-й курс")
#                 elif current_course == 2:
#                     transfered_students = len([s for s in selected_students_in_group if s.transfer_to_3rd_year_order == order_number])
#                     print(f"Переведено на 3-й курс: {transfered_students}")
#                     if students_count == transfered_students:
#                         group.current_course = 3
#                         group.save()
#                         print(f"Группа {group.id} переведена на 3-й курс")
#                 elif current_course == 3:
#                     transfered_students = len([s for s in selected_students_in_group if s.transfer_to_4th_year_order == order_number])
#                     print(f"Переведено на 4-й курс: {transfered_students}")
#                     if students_count == transfered_students:
#                         group.current_course = 4
#                         group.save()
#                         print(f"Группа {group.id} переведена на 4-й курс")
#
#         return redirect(self.success_url)
#
#     def form_invalid(self, form):
#         return super().form_invalid(form)


from django.db import transaction
from django.shortcuts import redirect

class PromoteStudentsView(PermissionBaseMixin, FormView):
    model = CurrentStudent
    form_class = PromoteStudentsForm
    template_name = "Contingent/transfer/transfer_students_form.html"
    success_url = reverse_lazy("transfer_students_form")
    permission_required = getpermission("Contingent", "transfer_students")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["properties"] = self.request.GET.dict()
        return kwargs

    def form_valid(self, form):
        students = form.cleaned_data.get("students")
        order_number = form.cleaned_data.get("order_number")
        print(f"PromoteStudentsView: Количество выбранных студентов: {len(students)}")
        print(f"PromoteStudentsView: ID студентов: {[student.id for student in students]}")
        print(f"PromoteStudentsView: Номер приказа: {order_number}")

        groups = set()

        with transaction.atomic():
            for student in students:
                try:
                    groups.add(student.group)
                    print(f"Обрабатываем студента {student.id}, группа {student.group.id}, курс группы {student.group.current_course}")
                    if student.group.current_course == 1:
                        student.transfer_to_2nd_year_order = order_number
                    elif student.group.current_course == 2:
                        student.transfer_to_3rd_year_order = order_number
                    elif student.group.current_course == 3:
                        student.transfer_to_4th_year_order = order_number
                    elif student.group.current_course == 4:
                        student.expell_order = order_number
                        student.is_expelled = True

                    create_transfer_log(order_number, student)
                    student.save()
                    print(f"Студент {student.id} сохранён")
                except Exception as e:
                    print(f"Ошибка при обработке студента {student.id}: {e}")
                    continue

            for group in groups:
                # Формируем список студентов текущей группы из выбранных в форме
                selected_students_in_group = [s for s in students if s.group == group]
                students_count = len(selected_students_in_group)
                current_course = group.current_course
                print(f"Группа {group.id}, курс {current_course}, выбрано студентов: {students_count}")

                if students_count == 0:
                    print(f"Пропускаем группу {group.id}, так как нет выбранных студентов")
                    continue

                # Проверяем, все ли студенты группы переведены на следующий курс
                if current_course == 1:
                    # Подсчитываем студентов, переведённых текущим приказом
                    transfered_students = len(
                        [s for s in selected_students_in_group if s.transfer_to_2nd_year_order == order_number])
                    # Подсчитываем всех непереведённых студентов в группе
                    remaining_students = Student.objects.filter(group=group,
                                                                transfer_to_2nd_year_order__isnull=True).count()
                    print(f"Переведено на 2-й курс текущим приказом: {transfered_students}")
                    print(f"Осталось перевести на 2-й курс: {remaining_students}")
                    # Если нет непереведённых студентов, обновляем курс группы
                    if remaining_students == 0:
                        group.current_course = 2
                        group.save()
                        print(f"Группа {group.id} переведена на 2-й курс")
                elif current_course == 2:
                    transfered_students = len(
                        [s for s in selected_students_in_group if s.transfer_to_3rd_year_order == order_number])
                    remaining_students = Student.objects.filter(group=group,
                                                                transfer_to_3rd_year_order__isnull=True).count()
                    print(f"Переведено на 3-й курс текущим приказом: {transfered_students}")
                    print(f"Осталось перевести на 3-й курс: {remaining_students}")
                    if remaining_students == 0:
                        group.current_course = 3
                        group.save()
                        print(f"Группа {group.id} переведена на 3-й курс")
                elif current_course == 3:
                    transfered_students = len(
                        [s for s in selected_students_in_group if s.transfer_to_4th_year_order == order_number])
                    remaining_students = Student.objects.filter(group=group,
                                                                transfer_to_4th_year_order__isnull=True).count()
                    print(f"Переведено на 4-й курс текущим приказом: {transfered_students}")
                    print(f"Осталось перевести на 4-й курс: {remaining_students}")
                    if remaining_students == 0:
                        group.current_course = 4
                        group.save()
                        print(f"Группа {group.id} переведена на 4-й курс")
                elif current_course == 4:
                    transfered_students = len([s for s in selected_students_in_group if s.is_expelled])
                    remaining_students = Student.objects.filter(group=group, is_expelled=False).count()
                    print(f"Отчислено текущим приказом: {transfered_students}")
                    print(f"Осталось отчислить: {remaining_students}")
                    if remaining_students == 0:
                        group.is_active = False
                        group.save()
                        print(f"Группа {group.id} деактивирована")

        return redirect(self.success_url)

    def form_invalid(self, form):
        return super().form_invalid(form)


class StudentDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации о студенте.
    """
    model= Student
    paginate_by  = 30
    template_name = 'Contingent/detail/student_detail.html'

    permission_required = getpermission('Contingent', 'view_current_student', 'view_expulsion_student', 'view_academ_student')

    fieldset = {
        'Основная информация':
            ['full_name', 'phone', 'birth_date', 'snils', 'course', 'group', 'admission_order', 'note'],
            
        'Образование':
            ['education_base', 'education_basis', 'transfer_to_2nd_year_order', 'transfer_to_3rd_year_order', 'transfer_to_4th_year_order', 'expelled_due_to_graduation', 'left_course'],
        
        'Контакты':
            ['registration_address', 'actual_address', 'representative_full_name', 'representative_email'],
    }

    buttons = [
        Button (
            id = 'change',
            name = 'Обновить',
            link_params = ['pk'],
            link_name = getpattern(Student, 'change'),
            permission = getpermission('Contingent', 'update_student')
        ),
    ]


class StudentUpdateView(ObjectUpdateView):
    """
    Класс для обновления информации о студенте.
    """
    form_class = StudentForm
    queryset = Student.objects.all()

    permission_required = getpermission('Contingent', 'update_student')

    buttons = [
        Button (
            id='to_object',
            name = 'К объекту',
            link_params = ['pk'],
            link_name = getpattern(Student, 'detail'),
            permission = getpermission('Contingent', 'update_student')
        ),
    ]


class StudentCreateView(ObjectCreateView):
    """
    Класс для создания нового студента.
    """
    model = Student
    form_class = StudentForm
    
    buttons = [
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(CurrentStudent, 'list'),
            permission = getpermission('Contingent', 'view_current_student')
        )
    ]

#
## Студенты в академе
#

class AcademUpdateView(ObjectUpdateView):
    """
    Класс для отправки студента в академ.
    """
    form_class = AcademLeaveForm
    queryset = Student.objects.filter(is_in_academ=False, is_expelled=False)

    permission_required = getpermission('Contingent', 'update_currentstudent')

class AcademListView(ObjectTableView):
    """
    Класс для просмотра студентов, находящихся в академе
    """
    table_class = AcademTable
    filterset_class = AcademFilter
    queryset = AcademStudent.objects.all()

    permission_required = getpermission('Contingent', 'view_academ_student')

class AcademReturn(ObjectUpdateView):
    """
    Класс для возвращения студента из академа
    """
    form_class = AcademReturnForm
    queryset = Student.objects.filter(is_in_academ=True, is_expelled=False)

    permission_required = getpermission('Contingent', 'return_currentstudent')

#
## Отчисленные студенты
#

class ExpulsionListView(ObjectTableView):
    table_class = ExpulsionTable
    filterset_class = ExpulsionFilter
    queryset = Student.objects.filter(is_expelled=True, is_in_academ=False)

    permission_required = getpermission('Contingent', 'view_expulsion_student')

# class ExpelStudent(ObjectUpdateView):
#     form_class = ExpellStudentForm
#     queryset = Student.objects.filter(is_in_academ=False, is_expelled=True)
#
#     permission_required = getpermission('Contingent', 'update_expulsion_student')

from django.contrib import messages
from django.shortcuts import redirect

class ExpelStudent(ObjectUpdateView):
    form_class = ExpellStudentForm
    queryset = Student.objects.filter(is_in_academ=False, is_expelled=False)
    permission_required = getpermission('Contingent', 'update_expulsion_student')


class RecoverStudent(ObjectUpdateView):
    form_class = RecoverStudentForm
    queryset = Student.objects.filter(is_in_academ=False, is_expelled=True)

    permission_required = getpermission('Contingent', 'return_expulsion_student')

#
## Статистика
#


class StatisticksView(ObjectTemplateView):
    template_name = 'Contingent/statisticks.html'

    permission_required = getpermission('Contingent', 'view_statistic')

    def get_context_data(self, **kwargs):
        student_list = student_format_to_list()
        specialty_data = defaultdict(lambda: defaultdict(int))
        all_specialties = list(Specialty.objects.all().values_list())
        print(all_specialties)

        # Инициализируем все направления заранее
        for qualification in Qualification.objects.all():
            specialty_data[(
                qualification.specialty.code, qualification.specialty.name, qualification.name)]  # Создаем пустые записи
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
            expelled = student["is_expelled"]

            if expelled:
                continue

            if base == "основное общее":
                base = 9
            else:
                base = 11

            if budget == "бюджет":
                budget = True
            else:
                budget = False

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

        last_row = [total_9_1_, total_9_2_, total_9_3_, total_9_4_, total_11_1_, total_11_2_, total_11_3_,
                    total_academ_1,
                    total_academ_2, total_academ_3, total_academ_4, total_contingent]

        total_1_09_02_07_budget = sum(
            counts.get(key, 0)
            for (code, _, _), counts in specialty_data.items()
            if code == "09.02.07"
            for key in counts
            if "budget" in key and key.startswith("students_9_1")
        )

        total_1_09_02_07_paid = sum(
            counts.get(key, 0)
            for (code, _, _), counts in specialty_data.items()
            if code == "09.02.07"
            for key in counts
            if "paid" in key and key.startswith("students_9_1")
        )

        context = super().get_context_data(**kwargs)
        context = context|{'table_data': table_data, 'last_row': last_row,
                   'total_09_02_07_budget': total_1_09_02_07_budget,
                   'total_09_02_07_paid': total_1_09_02_07_paid}

        return context

#
## Зачетка
#

class ViewRecordBookView(ObjectTemplateView):
    """
    Класс для отображения информации о зачетной книжке конкретного студента.
    """
    template_name = 'Contingent/record_book_view.html'

    permission_required = getpermission('Contingent', 'view_record_book')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем объекты
        qualification = get_object_or_404(Qualification, id=self.kwargs['qualification_id'])
        record_book = get_object_or_404(StudentRecordBook, student_id=self.kwargs['student_id'])
        context_record_book_object = create_template_recordbook_view(record_book)

        # Задаём контекст
        context['record_book'] = record_book  # Для основных данных студента
        context['qualification'] = qualification
        context['admission_year'] = self.kwargs['admission_year']
        context['url_list'] = 'student_list'
        context['is_student_gradebook'] = True
        context['student_id'] = self.kwargs['student_id']

        # Передаем данные из словаря напрямую
        context['middle_certifications'] = context_record_book_object['middle_certifications']
        context['professional_modules'] = context_record_book_object['professional_modules']
        context['practices'] = context_record_book_object['practices']
        context['term_papers'] = context_record_book_object['term_papers']
        context['semesters'] = context_record_book_object['semesters']

        # Определяем fieldset для табов
        context['fieldset'] = {
            'Информация': [],  # Поля будем отображать вручную в шаблоне
            'Промежуточная аттестация': ['middle_certifications'],
            'Профессиональные модули': ['professional_modules'],
            'Практики': ['practices'],
            'Курсовые работы': ['term_papers'],
        }

        return context

@permission_required(getpermission('Contingent', 'save_record_book'))
def generate_student_record_book(request, pk):
    """
    Функция для генерации зачетной книжки для конкретного студента
    """
    try:
        student = get_object_or_404(Student, pk=pk)
    except StudentRecordBook.DoesNotExist as e:
        print("Студент не найден")
    qualification = student.group.qualification
    admission_year = student.group.year_create

    print(qualification, admission_year)
    try:
        template = get_object_or_404(RecordBookTemplate, qualification=qualification, admission_year=admission_year)
    except RecordBookTemplate.DoesNotExist as e:
        print("Шаблон не найден")

    # Генерация уникального номера зачетки
    record_book_number = generate_unique_record_book_number(admission_year, student)
    print(2)
    # Создаём новый объект StudentRecordBook для студента
    new_record_book = StudentRecordBook.objects.create(
        student=student,
        qualification=qualification,
        admission_year=admission_year,
        student_name=f"{student.full_name}",
        record_book_number=record_book_number,
        admission_order=student.admission_order,
        issue_date=template.issue_date,
        curriculum=template.curriculum
    )
    print(new_record_book)
    student.record_book = new_record_book
    student.save()

    return redirect('view_record_book', qualification_id=qualification.id, admission_year=admission_year, student_id=pk)


@permission_required(getpermission('Contingent', 'save_record_book_template'))
def create_auto_record_book_template(request, qualification_id, admission_year):
    """
    Функция для генерации Шаблона зачетной книжки  шаблон генерируется на квалификацию и год поступления,
    Например для всех групп П 2021 года поступления
    """
    qualification = get_object_or_404(Qualification, id=qualification_id)
    curriculum = get_object_or_404(Curriculum, qualification=qualification, admission_year=admission_year)

    # Проверяем, существует ли шаблон, чтобы не дублировать
    if RecordBookTemplate.objects.filter(qualification=qualification, admission_year=admission_year).exists():
        return redirect('view_record_book_template', qualification_id=qualification_id, admission_year=admission_year)

    # Создаём шаблон
    template = RecordBookTemplate.objects.create(
        qualification=qualification,
        admission_year=admission_year,
        student_name="",  # Пустое, так как это шаблон
        record_book_number="",  # Пустое для шаблона
        admission_order="Не указан",  # Можно заполнить позже
        issue_date=datetime.now().date(),
        curriculum=curriculum
    )

    return redirect('view_record_book_template', qualification_id=qualification_id, admission_year=admission_year)


@permission_required(getpermission('Contingent', 'save_record_book'))
def generate_group_recordbooks(request, group_id):
    """
    Функция для генерации зачетных книжек на всю группу
    """
    group = get_object_or_404(GroupStudents, id=group_id)
    qualification = group.qualification
    admission_year = group.year_create

    # проверка на то что шаблон есть
    if not RecordBookTemplate.objects.filter(qualification=qualification, admission_year=admission_year).exists():
        create_auto_record_book_template(request, qualification.id, admission_year)

    template = get_object_or_404(RecordBookTemplate, qualification=qualification, admission_year=admission_year)
    students = group.students.all()

    for student in students:
        # if student.record_book:  # Пропускаем студентов с уже существующей зачёткой
        #     continue

        record_book_number = generate_unique_record_book_number(admission_year, student)
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

        student.record_book = new_record_book
        student.save()

    return redirect('groupstudents_detail', pk=group_id)


#########
#######Движения контингента
#########


class ContingentMovementTableView(ObjectTableView):
    """
    Класс для отображения таблицы движений контингента.
    """
    paginate_by = 10
    table_class = ContingentMovementTable
    filterset_class = ContingentMovementFilter
    queryset = ContingentMovement.objects.all()
    template_name = 'Contingent/contingent_movement_list.html'

    permission_required = getpermission('Contingent', 'view_movement')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_name'] = "Движения контингента"
        return context


#########
#######Обработка генерации доков
#########

@permission_required(getpermission('Contingent', 'export_group_student'))
def generate_group_table(request):
    """
    Функция для генерации файла .xslx для всех групп
    """
    groups = GroupStudents.objects.all()
    generator = GroupTableGenerator(groups)
    file_path = os.path.join(settings.MEDIA_ROOT, 'group_table.xlsx')

    # Создаём директорию, если она не существует
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    generator.generate_document(file_path)

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="group_table.xlsx"'

    os.remove(file_path)  # Удаляем временный файл после отправки
    return response


@permission_required(getpermission(Student, 'export'))
def generate_course_table(request, course):
    """
    Функция для генерации файла .xslx для статистики по определенному курсу
    """
    students = Student.objects.filter(group__current_course=course)
    # try:
    generator = CourseTableGenerator(students)
    file_path = os.path.join(settings.MEDIA_ROOT, f'course_{course}_table.xlsx')

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    generator.generate_document(file_path)

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="course_{course}_table.xlsx"'
    os.remove(file_path)
    return response
    # except (CourseDifferenceError, EducationBaseDifferenceError) as e:
    #     return HttpResponse(f"Ошибка: {e.message}", status=400)

@permission_required(getpermission('Contingent', 'export_statistic'))
def generate_statistics_table(request):
    """
    Функция для генерации файла .xslx для статистики
    """
    specialties = Specialty.objects.all()
    qualifications = Qualification.objects.all()
    students = Student.objects.all()
    generator = StatisticsTableGenerator(specialties, qualifications, students)
    file_path = os.path.join(settings.MEDIA_ROOT, 'statistics_table.xlsx')

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    generator.generate_document(file_path)

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="statistics_table.xlsx"'
    os.remove(file_path)
    return response

@permission_required(getpermission('Contingent', 'export_statistic'))
def generate_vacation_table(request):
    """
    Функция для генерации файла .xslx для студентов находящихся в академическом отпуске
    """
    students = Student.objects.filter(is_in_academ=True)
    generator = VacationTableGenerator(students)
    file_path = os.path.join(settings.MEDIA_ROOT, 'vacation_table.xlsx')

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    generator.generate_document(file_path)

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="vacation_table.xlsx"'
    os.remove(file_path)
    return response


@permission_required(getpermission('Contingent', 'export_movement'))
def generate_movement_table(request):
    """
    Функция для генерации файла .xslx для движения кнтингента
    """
    movements = ContingentMovement.objects.all()  # Получаем все записи о движениях
    generator = MovementTableGenerator(movements)
    file_path = os.path.join(settings.MEDIA_ROOT, 'movement_table.xlsx')

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    generator.generate_document(file_path)

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="movement_table.xlsx"'
    os.remove(file_path)
    return response


#
## Создание шаблона зачеток для учебного плана
#

class GenerateQualificationTemplate(PermissionBaseMixin, FormView):
    permission_required = getpermission('Contingent', 'generate_qualification_template')
    template_name = 'Contingent/generate_qualification_template.html'
    form_class = GenerateQualificationTemplateForm

    def form_invalid(self, form):
        # Собираем все ошибки формы в одно сообщение
        error_messages = []
        
        # Общие ошибки формы (non-field errors)
        for error in form.non_field_errors():
            error_messages.append(error)
        
        # Объединяем все ошибки в одно сообщение
        if error_messages:
            messages.error(self.request, "Ошибки в форме:\n" + "\n".join(error_messages))
        
        return super().form_invalid(form)
    
    def form_valid(self, form):
        messages.success(self.request, "Шаблон успешно создан")
        return redirect('generate_qualification_template')