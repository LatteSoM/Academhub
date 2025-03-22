from Gradebook.forms import *
from Gradebook.tables import *
from Gradebook.filters import *
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from Gradebook.mixins import GradeBookMixin
from Gradebook.tables import TeacherGradeBookTable
from Academhub.utils import getpermission, getpattern
from Gradebook.filters import GradeBookTeachersFilter
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from Academhub.models import GradebookStudents, Gradebook, CustomUser, SubTable, Button
from Academhub.generic import BulkUpdateView, ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView

#
# Create your views here.
#

__all__ = (
    'download_report',
    'GradebookTableView',
    'GradebookClosedList',
    'GradebookDetailView',
    'GradebookCreateView',
    'GradebookUpdateView',
    'check_and_open_gradebook',
    'TeachersGradeBookTableView',
    'GradebookStudentBulkUpdateView',
)

class GradebookStudentBulkUpdateView(BulkUpdateView):
    model = GradebookStudents
    form_class = GradebookStudentsForm
    template_name = 'Gradebook/create/grade_book_students.html'

    def dispatch(self, request, *args, **kwargs):
        self.gradebook_pk = self.kwargs.get('pk', None)
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.model.objects.filter(gradebook__pk = self.gradebook_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.gradebook = get_object_or_404(Gradebook, pk=self.gradebook_pk)
        context['gradebook'] = self.gradebook
        return context
    
    def save_form(self, request):
        form = super().save_form(request)

        if form.is_valid():
            gradebook = get_object_or_404(
                Gradebook, 
                pk=self.gradebook_pk
            )
            gradebook.status = Gradebook.STATUS_CHOICE[2][1]
            gradebook.date_of_filling = timezone.now()
            gradebook.save()

        return form

    def post(self, request, *args, **kwargs):
        formset = self.save_form(request)

        if formset.is_valid():
            user = get_object_or_404(CustomUser, pk=self.request.user.pk)

            if user.is_teacher:
                response = redirect('gradebookteacher_list')
            else:
                response = redirect('gradebook_list')
            response['Location'] += '?is_filled=true'
            return response
        return super().post(request, *args, **kwargs)


class GradebookTableView(ObjectTableView):
    """
    Класс для отображения таблицы учебных журналов.
    """
    table_class = GradebookTable
    filterset_class = GradebookFilter
    queryset = Gradebook.objects.all()

    buttons = [
        Button (
            id='add',
            name = 'Добавить',
            link_name = getpattern(Gradebook, 'add'),
            permission = getpermission(Gradebook, 'add'),
        )
    ]
    queryset = Gradebook.objects.exclude(status=Gradebook.STATUS_CHOICE[3][1])

    def get_table_class(self):
        if self.request.GET.get("mobile") == "1":
            return GradebookMobileTable
        return GradebookTable

    def get(self, request, *args, **kwargs):

        is_closed = request.GET.get('is_closed', None)
        is_filled = request.GET.get('is_filled', None)

        if is_closed:
            messages.success(request, "Ведомость успешно закрыта!")
        if is_filled:
            messages.success(request, "Ведомость успешно заполнена!")

        return super().get(request, *args, **kwargs)


class GradebookClosedList(ObjectTableView):
    table_class = GradebookTable
    filterset_class = GradebookFilter
    queryset = Gradebook.objects.filter(status=Gradebook.STATUS_CHOICE[3][1])
    properties = {}

    def get_table_class(self):
        if self.request.GET.get("mobile") == "1":
            return GradebookMobileTable
        return GradebookTable

class TeachersGradeBookTableView(ObjectTableView):
    permission_required = None
    table_class = TeacherGradeBookTable
    filterset_class = GradeBookTeachersFilter
    queryset = Gradebook.objects.all() 

    def get_queryset(self):
        # Получаем залогиненного пользователя
        user = get_object_or_404(CustomUser, pk=self.request.user.pk)

        # Проверка аутентификации и прав преподавателя
        if not user.is_authenticated or not hasattr(user, 'is_teacher') or not user.is_teacher:
            return Gradebook.objects.none()

        # Фильтрация ведомостей
        queryset = Gradebook.objects.filter(
            status='Открыта',  # Статус "Открыта"
            teachers__id=user.id  # Текущий пользователь в списке преподавателей
        ).select_related(  # Оптимизация запросов
            'group',
            'discipline'
        ).prefetch_related(
            'teachers',
            'students'
        ).distinct()  # Убираем дубликаты

        return queryset
 
    def get_table_class(self):
        if self.request.GET.get("mobile") == "1":
            return GradebookMobileTable
        return TeacherGradeBookTable

    def get(self, request, *args, **kwargs):

        is_filled = request.GET.get('is_filled', None)

        if is_filled:
            messages.success(request, "Ведомость успешно заполнена!")

        return super().get(request, *args, **kwargs)

class GradebookDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации об учебном журнале.
    """
    model= Gradebook
    paginate_by   = 30
    template_name = 'Gradebook/detail/gradebook_student.html'

    fieldset = {
        'Основная информация': [
            'name', 'status'
        ],
    }

    buttons = [
        Button (
            id = 'change',
            link_params = ['pk'],
            link_name = getpattern(Gradebook, 'change'),
            permission = getpermission(Gradebook, 'change'),
        ),
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Gradebook, 'list'),
            permission = getpermission(Gradebook, 'view')
        )
    ]

    def grade_book_student_filter(self, queryset):
        if queryset.filter(gradebook_id=self.pk).count() == 0:
            return GradebookStudents.objects.filter(gradebook=self.pk)
        return queryset.filter(gradebook__id=self.pk)

    def grade_book_teacher_filter(self, queryset):
        return self.teachers.all()

    tables = [
        SubTable (
            name='Студенты',
            table=GradebookStudentsTable,
            queryset=GradebookStudents.objects.all(),
            filter_func=grade_book_student_filter,
            buttons=[
                Button (
                    name = 'Заполнить ведомость',
                    link_name = 'gradebookstudents_bulk_create',
                    link_params = ['pk']
                )
            ]
        ),
        SubTable(
            name='Учителя',
            queryset=CustomUser.objects.all(),
            table=GradebookTeachersTable,
            filter_func=grade_book_teacher_filter
        )
    ]

    def get(self, request, *args, **kwargs):
        gradebook = self.get_object()

        is_active = request.GET.get('is_active',None)

        # Проверка основных полей
        required_fields = [
            gradebook.group_id,  # Проверка ForeignKey через id
            gradebook.name,  # Проверка CharField
            gradebook.discipline_id,  # Проверка ForeignKey дисциплины
            gradebook.semester_number,  # Проверка IntegerField
            gradebook.status,  # Проверка CharField статуса
        ]

        # Проверка текстовых полей на непустые значения
        text_fields_valid = all([
            gradebook.name and gradebook.name.strip(),
            gradebook.status and gradebook.status.strip(),
        ])

        relations_valid = all([
            gradebook.teachers.exists(),  # Проверка наличия преподавателей
            gradebook.students.exists(),  # Проверка наличия студентов
        ])

        # Комплексная проверка всех условий
        if not all(required_fields) or not text_fields_valid or not relations_valid:
            messages.error(
                request,
                "Невозможно открыть ведомость! Заполните все обязательные поля: "
                "группа, дисциплина, название, статус, семестр, преподаватели и студенты."
            )
        else:
            if is_active:
                messages.success(request, "Ведомость успешно открыта!")

        return super().get(request, *args, **kwargs)


class GradebookUpdateView(GradeBookMixin, ObjectUpdateView):
    form_class = GradebookForm  # Используем обновленную форму
    queryset = Gradebook.objects.all()
    properties = {}

    buttons = [
        Button (
            id='to_object',
            name = 'К объекту',
            link_params = ['pk'],
            link_name = getpattern(Gradebook, 'detail'),
            permission = getpermission(Gradebook, 'view')
        ),
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Gradebook, 'list'),
            permission = getpermission(Gradebook, 'view')
        )
    ]

    # Убираем ненужные свойства
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('properties', None)  # Удаляем параметр properties
        return kwargs


class GradebookCreateView(GradeBookMixin, ObjectCreateView):
    """
    Класс для создания нового учебного журнала.
    """
    model = Gradebook
    form_class = GradebookForm
    template_name = 'Gradebook/create/grade_book.html'
    properties = ['group_id']

    buttons = [
        Button (
            id = 'to_list',
            name = 'К таблице',
            link_name = getpattern(Gradebook, 'list'),
            permission = getpermission(Gradebook, 'view')
        )
    ]


@permission_required(getpermission(Gradebook, 'view'))
def download_report(request, pk):
    gradebook = get_object_or_404(Gradebook, pk=pk)

    response = redirect('gradebook_list')
    if gradebook.status == Gradebook.STATUS_CHOICE[2][1]:
        response['Location'] += '?is_closed=true'
    gradebook.status = Gradebook.STATUS_CHOICE[3][1]
    gradebook.date_of_closing = timezone.now()
    gradebook.save()

    # TODO: Присрать Васин модуль генерации ведомости

    return response

@permission_required(getpermission(Gradebook, 'view'))
def check_and_open_gradebook(request, pk):
    """
    Проверяет заполненность всех обязательных полей ведомости,
    включая наличие связанных преподавателей и студентов.
    """
    gradebook = get_object_or_404(Gradebook, id=pk)

    # Проверка основных полей
    required_fields = [
        gradebook.group_id,  # Проверка ForeignKey через id
        gradebook.name,  # Проверка CharField
        gradebook.discipline_id,  # Проверка ForeignKey дисциплины
        gradebook.semester_number,  # Проверка IntegerField
        gradebook.status,  # Проверка CharField статуса
    ]

    # Проверка текстовых полей на непустые значения
    text_fields_valid = all([
        gradebook.name and gradebook.name.strip(),
        gradebook.status and gradebook.status.strip(),
    ])

    # Проверка связей ManyToMany и ForeignKey
    relations_valid = all([
        gradebook.teachers.exists(),  # Проверка наличия преподавателей
        gradebook.students.exists(),  # Проверка наличия студентов
    ])

    # Комплексная проверка всех условий
    if not all(required_fields) or not text_fields_valid or not relations_valid:
        return redirect('gradebook_detail', pk=pk)

    # Обновление статуса и даты
    gradebook.status = "Открыта"
    gradebook.date_of_opening = timezone.now().date()
    gradebook.save()

    response = redirect('gradebook_detail', pk=pk)
    response['Location'] += '?is_active=true'
    return response

