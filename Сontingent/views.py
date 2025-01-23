from .models import *
from .tables import *
from .filters import *
from .forms import StudentForm
from django.shortcuts import render
from Academhub.base import ObjectTableView, ObjectUpdateView, DeleteView, ObjectDetailView, ObjectCreateView
# Create your views here.

#
## Qualification
#

class QualificationTableView(ObjectTableView):
    table_class = QualificationTable
    filterset_class = QualificationFilter
    queryset = QualificationDTO.objects.all()

#
## Specialization
#

class SpecializationTableView(ObjectTableView):
    table_class = SpecializationTable
    filterset_class = SpecializationFilter
    queryset = SpecializationDTO.objects.all()

#
## Group
#

class GroupTableView(ObjectTableView):
    table_class = GroupTable
    filterset_class = GroupFilter
    queryset = GroupDTO.objects.all()

#
## Student
#

class StudentTableView(ObjectTableView):
    table_class = StudentTable
    filterset_class = StudentFilter
    queryset = StudentDTO.objects.all()

class StudentDeleteView(DeleteView):
    queryset = StudentDTO.objects.all()

class StudentDetailView(ObjectDetailView):
    model= StudentDTO

class StudentUpdateView(ObjectUpdateView):
    form_class = StudentForm
    queryset = StudentDTO.objects.all()

class StudentCreateView(ObjectCreateView):
    model = StudentDTO
    form_class = StudentForm