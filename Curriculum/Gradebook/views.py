from django.http import FileResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, SingleTableView
from xhtml2pdf import pisa

from Curriculum.base.generic import ObjectCreateView, ObjectUpdateView, ObjectDetailView, ObjectListView, \
    ObjectTemplateView
from Curriculum.Gradebook.filters import GradebookFilter, GradeBookTeachersFilter
from Curriculum.Gradebook.forms import GradebookForm, GradebookStudentsForm
from Curriculum.Gradebook.mixins import GradeBookMixin
from Curriculum.Gradebook.tables import GradebookTable, GradebookStudentsTable, GradebookTeachersTable, \
    TeacherGradeBookTable
from Curriculum.models import Gradebook, GradebookStudents


class GradebookStudentBulkUpdateView(GradeBookMixin, SingleTableMixin, FilterView):
    """
    Представление для массового обновления оценок студентов в ведомости.
    """
    template_name = 'Gradebook/update/gradebook_students_form.html'
    formset_class = None
    model = GradebookStudents
    table_class = GradebookStudentsTable
    filterset_class = None

    def dispatch(self, request, *args, **kwargs):
        gradebook = get_object_or_404(Gradebook, pk=self.kwargs.get('pk'))
        if gradebook.teacher != request.user:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        gradebook = get_object_or_404(Gradebook, pk=self.kwargs.get('pk'))
        return gradebook.students.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gradebook'] = get_object_or_404(Gradebook, pk=self.kwargs.get('pk'))
        context['formset'] = self.formset_class(queryset=self.get_queryset())
        return context

    def save_form(self, request):
        gradebook = get_object_or_404(Gradebook, pk=self.kwargs.get('pk'))
        self.formset_class = forms.modelformset_factory(GradebookStudents, form=GradebookStudentsForm, extra=0)
        formset = self.formset_class(request.POST, queryset=self.get_queryset())
        if formset.is_valid():
            formset.save()
            return True
        return False

    def post(self, request, *args, **kwargs):
        if self.save_form(request):
            return redirect('gradebook_detail', pk=self.kwargs.get('pk'))
        else:
            return self.get(request)


class GradebookTableView(ObjectTableView):
    """
    Представление для отображения таблицы ведомостей.
    """
    model = Gradebook
    template_name = 'Gradebook/list/gradebook_list.html'
    filterset_class = GradebookFilter

    def get_table_class(self):
        if self.request.user.is_staff:
            return GradebookTable
        else:
            return TeacherGradeBookTable


class TeachersGradeBookTableView(ObjectTableView):
    """
    Представление для отображения таблицы ведомостей.
    """
    model = Gradebook
    template_name = 'Gradebook/list/gradebook_list.html'
    filterset_class = GradeBookTeachersFilter

    def get_table_class(self):
        if self.request.user.is_staff:
            return GradebookTable
        else:
            return TeacherGradeBookTable


class GradebookDetailView(ObjectDetailView):
    """
    Представление для отображения детальной информации о ведомости.
    """
    model = Gradebook
    template_name = 'Gradebook/detail/gradebook_detail.html'
    sub_tables = []

    def grade_book_student_filter(object, queryset):
        return queryset.filter(gradebookstudents__gradebook=object)

    def grade_book_teacher_filter(object, queryset):
        return queryset.filter(gradebook__teacher=object)

    sub_tables = [
        {
            'table': GradebookStudentsTable,
            'queryset': GradebookStudents.objects.all(),
            'name': 'Студенты',
            'filter_key': 'gradebook',
            'filter_func': grade_book_student_filter
        },
    ]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class GradebookUpdateView(GradeBookMixin, ObjectUpdateView):
    """
    Представление для обновления ведомости.
    """
    model = Gradebook
    form_class = GradebookForm
    template_name = 'Gradebook/update/gradebook_form.html'


class GradebookCreateView(GradeBookMixin, ObjectCreateView):
    """
    Представление для создания ведомости.
    """
    model = Gradebook
    form_class = GradebookForm
    template_name = 'Gradebook/create/gradebook_form.html'


def download_report(request, pk):
    gradebook = get_object_or_404(Gradebook, pk=pk)

    # Получаем шаблон
    template = get_template('Gradebook/inc/report_template.html')

    # Формируем контекст
    context = {
        'gradebook': gradebook,
    }

    # Рендерим шаблон
    html = template.render(context)

    # Создаем PDF
    response = FileResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    pisa.CreatePDF(html, dest=response)

    return response


def check_and_open_gradebook(request, pk):
    gradebook = get_object_or_404(Gradebook, pk=pk)
    if gradebook.teacher == request.user or request.user.is_staff:
        return redirect('gradebook_detail', pk=pk)
    else:
        return redirect('home')