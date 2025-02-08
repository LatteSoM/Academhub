from .forms import *
from .tables import *
from .filters import *
from django_tables2 import RequestConfig
from Academhub.models import GroupStudents, Qualification, Specialty, Student
from Academhub.base import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView

#
## Specialty
#

class SpecialtyTableView(ObjectTableView):
    table_class = SpecialtyTable
    filterset_class = SpecialtyFilter
    queryset = Specialty.objects.all()

class SpecialtyDetailView(ObjectDetailView):
    model= Specialty
    pagination_by = 30
    template_name = 'Contingent/specialty_detail.html'

    def get_table(self):
        students = Qualification.objects.filter(specialty__pk=self.object.pk)
        table = QualificationTable(data=students)
        return table

class SpecialtyUpdateView(ObjectUpdateView):
    form_class = SpecialtyForm
    queryset = Specialty.objects.all()

class SpecialtyCreateView(ObjectCreateView):
    model = Specialty
    form_class = SpecialtyForm

#
## Qualification
#

class QualificationTableView(ObjectTableView):
    table_class = QualificationTable
    filterset_class = QualificationFilter
    queryset = Qualification.objects.all()

class QualificationTableView(ObjectTableView):
    table_class = QualificationTable
    filterset_class = QualificationFilter
    queryset = Qualification.objects.all()

class QualificationDetailView(ObjectDetailView):
    model= Qualification
    pagination_by = 30
    template_name = 'Contingent/qualification_detail.html'

    def get_table(self):
        students = GroupStudents.objects.filter(qualification__pk=self.object.pk)
        table = GroupTable(data=students)
        return table

class QualificationUpdateView(ObjectUpdateView):
    form_class = QualificationForm
    queryset = Qualification.objects.all()

class QualificationCreateView(ObjectCreateView):
    model = Qualification
    form_class = QualificationForm


#
## Group
#

class GroupTableView(ObjectTableView):
    table_class = GroupTable
    filterset_class = GroupFilter
    queryset = GroupStudents.objects.all()

class GroupDetailView(ObjectDetailView):
    pagination_by = 30
    model= GroupStudents
    template_name = 'Contingent/group_detail.html'

    def get_table(self):

        students = Student.objects.filter(group__pk=self.object.pk)
        table = StudentTable2(data=students)

        return table

class GroupUpdateView(ObjectUpdateView):
    form_class = GroupForm
    queryset = GroupStudents.objects.all()

class GroupCreateView(ObjectCreateView):
    model = GroupStudents
    form_class = GroupForm

#
## Student
#

class StudentTableView(ObjectTableView):
    table_class = StudentTable
    filterset_class = StudentFilter
    queryset = Student.objects.all()

class StudentDetailView(ObjectDetailView):
    model= Student
    pagination_by = 30
    template_name = 'Contingent/student_detail.html'

class StudentUpdateView(ObjectUpdateView):
    form_class = StudentForm
    queryset = Student.objects.all()

class StudentCreateView(ObjectCreateView):
    model = Student
    form_class = StudentForm