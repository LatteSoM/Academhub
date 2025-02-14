from django.shortcuts import render
from Academhub.base import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView
from Gradebook.filters import *
from Gradebook.forms import *
from Gradebook.tables import *



# Create your views here.

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

    fieldset = {
        'Основная информация':
            ['name', 'teacher', 'status', ]
    }

class GradebookUpdateView(ObjectUpdateView):
    """
    Класс для обновления информации об учебном журнале.
    """
    form_class = GradebookForm
    queryset = Gradebook.objects.all()

class GradebookCreateView(ObjectCreateView):
    """
    Класс для создания нового учебного журнала.
    """
    model = Gradebook
    form_class = GradebookForm
    template_name = 'Gradebook/create/grade_book.html'
    properties = {
        'group_id': ''
    }

    def get_properties(self, request):
        """
        Получает id группы из запроса и сохраняет его в словаре properties.
        """
        self.properties['group_id'] = request.GET.get('group_id')

    def get_form_kwargs(self):
        """
        Добавляет словарь properties в аргументы формы.
        """
        kwargs = super().get_form_kwargs()
        kwargs['properties'] = self.properties
        return kwargs

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос.
        """
        self.get_properties(request)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос.
        """
        self.get_properties(request)
        return super().post(request, *args, **kwargs)
