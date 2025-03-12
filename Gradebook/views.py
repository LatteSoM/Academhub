from Gradebook.forms import *
from Gradebook.tables import *
from Gradebook.filters import *
from Gradebook.mixins import GradeBookMixin
from django.shortcuts import get_object_or_404, redirect
from Academhub.models import GradebookStudents, Gradebook
from Academhub.base import BulkUpdateView, ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView

#
# Create your views here.
#

__all__ = (
    'GradebookTableView',
    'GradebookDetailView',
    'GradebookCreateView',
    'GradebookUpdateView',
    # 'GradebookDisciplineCreateView',
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
            gradebook.status = Gradebook.STATUS_CHOICE[1][1]
            gradebook.save()

        return form

    def post(self, request, *args, **kwargs):
        formset = self.save_form(request)

        if formset.is_valid():
            return redirect('gradebook_detail', pk=self.gradebook_pk)
        return super().post(request, *args, **kwargs)

#
## Gradebook
#

class GradebookTableView(ObjectTableView):
    """
    Класс для отображения таблицы учебных журналов.
    """
    table_class = GradebookTable
    filterset_class = GradebookFilter
    queryset = Gradebook.objects.all()

    def get_table_class(self):
        if self.request.GET.get("mobile") == "1":
            return GradebookMobileTable
        return GradebookTable

class GradebookDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации об учебном журнале.
    """
    model= Gradebook
    paginate_by   = 30
    template_name = 'Gradebook/detail/gradebook_student.html'

    fieldset = {
        'Основная информация':
            ['name', 'status', ]
    }

    def get_tables(self):
        table = GradebookStudentsTable(data=self.object.students.all())
        # print(table.student)

        table2 = GradebookTeachersTable(data=self.object.teachers.all())
        # print(table2)
        
        return [table, table2]

class GradebookUpdateView(GradeBookMixin, ObjectUpdateView):
    """
    Класс для обновления информации об учебном журнале.
    """
    form_class = GradebookForm
    queryset = Gradebook.objects.all()
    template_name = 'Gradebook/update/grade_book.html'
    properties = {
        'group_id': ''
    }



class GradebookCreateView(GradeBookMixin, ObjectCreateView):
    """
    Класс для создания нового учебного журнала.
    """
    model = Gradebook
    form_class = GradebookForm
    template_name = 'Gradebook/create/grade_book.html'
    properties = ['group_id']

# class GradebookDisciplineCreateView(GradeBookMixin, ObjectCreateView):
#     """
#     Класс для создания нового учебного журнала.
#     """
#     model = Gradebook
#     form_class = GradebookForm
#     template_name = 'Gradebook/create/grade_book.html'
#     properties = ['group_id', 'discipile_id']