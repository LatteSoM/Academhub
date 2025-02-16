from Gradebook.forms import *
from Gradebook.tables import *
from Gradebook.filters import *
from Gradebook.mixins import GradeBookMixin
from django.shortcuts import get_object_or_404
from Academhub.models import GradebookStudents
from Academhub.base import BulkUpdateView, ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView

#
# Create your views here.
#

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

    # def get_table_class(self):
    #     """Определяет, какую таблицу использовать (мобильную или десктопную)."""
    #     user_agent = self.request.META.get('HTTP_USER_AGENT', '').lower()
    #     if 'mobile' in user_agent:
    #         return GradebookMobileTable
    #     return GradebookMobileTable

class GradebookDetailView(ObjectDetailView):
    """
    Класс для отображения детальной информации об учебном журнале.
    """
    model= Gradebook
    paginate_by   = 30
    template_name = 'Gradebook/detail/gradebook_student.html'

    fieldset = {
        'Основная информация':
            ['name', 'teacher', 'status', ]
    }

    def get_table(self):
        students = GradebookStudents.objects.filter(gradebook__pk=self.object.pk)
        table = GradebookStudentsTable(data=students)
        return table

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
    properties = {
        'group_id': ''
    }
