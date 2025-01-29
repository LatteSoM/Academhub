from django.views.generic import DeleteView

from Academhub.base import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView
from Academhub.models import Group, Qualification, Specialty, Student
# TODO
## - from Academhub.models import *
from .filters import *
from .forms import StudentForm
from .tables import *


# Create your views here.

#
## Qualification
#

class QualificationTableView(ObjectTableView):
    table_class = QualificationTable
    filterset_class = QualificationFilter
    queryset = Qualification.objects.all()

#
## Specialization
#

class SpecializationTableView(ObjectTableView):
    table_class = SpecializationTable
    filterset_class = SpecializationFilter
    queryset = Specialty.objects.all()

#
## Group
#

class GroupTableView(ObjectTableView):
    table_class = GroupTable
    filterset_class = GroupFilter
    queryset = Group.objects.all()

#
## Student
#

class StudentTableView(ObjectTableView):
    table_class = StudentTable
    filterset_class = StudentFilter
    queryset = Student.objects.all()

class StudentDeleteView(DeleteView):
    queryset = Student.objects.all()

class StudentDetailView(ObjectDetailView):
    model= Student

class StudentUpdateView(ObjectUpdateView):
    form_class = StudentForm
    queryset = Student.objects.all()

class StudentCreateView(ObjectCreateView):
    model = Student
    form_class = StudentForm