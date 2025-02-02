from Academhub.base import ObjectTableView, ObjectDetailView, ObjectUpdateView, ObjectCreateView
from Academhub.models import GroupStudents, Qualification, Specialty, Student
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
## Specialty
#

class SpecialtyTableView(ObjectTableView):
    table_class = SpecialtyTable
    filterset_class = SpecialtyFilter
    queryset = Specialty.objects.all()

#
## Group
#

class GroupTableView(ObjectTableView):
    table_class = GroupTable
    filterset_class = GroupFilter
    queryset = GroupStudents.objects.all()

#
## Student
#

class StudentTableView(ObjectTableView):
    table_class = StudentTable
    filterset_class = StudentFilter
    queryset = Student.objects.all()

class StudentDetailView(ObjectDetailView):
    model= Student

class StudentUpdateView(ObjectUpdateView):
    form_class = StudentForm
    queryset = Student.objects.all()

class StudentCreateView(ObjectCreateView):
    model = Student
    form_class = StudentForm