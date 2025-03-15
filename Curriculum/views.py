from django.shortcuts import render
from Academhub.base import BulkUpdateView, ObjectTableView, ObjectListView
# from parser_for_plx import RUP_parser
from django.shortcuts import render
from .forms import GetPlxForm
# Create your views here.




def curriculum_list(request):
    form = GetPlxForm(request.POST, request.FILES)
    return render(request=request, template_name="Curriculum/list/curriculums.html", context={'form': form})


