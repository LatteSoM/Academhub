from .models import *
from .tables import *
from .filters import *
from django.shortcuts import render
from Academhub.base.generic import ObjectTableView
# Create your views here.

#
## Qualification
#

class QualificationTableView(ObjectTableView):
    table_class = QualificationTable
    filterset_class = QualificationFilter
    queryset = QualificationDTO.objects.all()
    template_name = 'Contingent/qualification.html'

#
## Specialization
#

class SpecializationTableView(ObjectTableView):
    table_class = SpecializationTable
    filterset_class = SpecializationFilter
    queryset = SpecializationDTO.objects.all()
    template_name = 'Contingent/specialization.html'

#
## Group
#

class GroupTableView(ObjectTableView):
    table_class = GroupTable
    filterset_class = GroupFilter
    queryset = GroupDTO.objects.all()
    template_name = 'Contingent/group.html'

#
## Student
#

class StudentTableView(ObjectTableView):
    table_class = StudentTable
    filterset_class = StudentFilter
    queryset = StudentDTO.objects.all()
    template_name = 'Contingent/students.html'