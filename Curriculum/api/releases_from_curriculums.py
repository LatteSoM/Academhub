import json
from http.client import responses

import pandas as pd
from django.db import transaction
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from Academhub.models.models import ReleaseCell
from Gradebook.utils import update_gradebooks_after_deactivation
from Academhub.models import Qualification, Curriculum, GroupStudents, ClockCell, CustomUser, ReleaseFromCurriculum, \
    TeachersForDisciplineAndCurriculum

semester_dict = {
        "1-1": 1,
        "1-2": 2,
        "2-1": 3,
        "2-2": 4,
        "3-1": 5,
        "3-2": 6,
        "4-1": 7,
        "4-2": 8,
    }



def get_study_plans_by_qualification(request):
    qualification_id = request.GET.get('qualification_id')
    if not qualification_id or qualification_id == 'Выберите квалификацию':
        return JsonResponse({'error': 'Missing qualification_id'}, status=400)

    qualification = Qualification.objects.get(id=qualification_id)

    curriculums = []

    for curriculum in qualification.curriculums.all():
        curriculums.append({
            "id": curriculum.id,
            "qualification_name": curriculum.qualification_name,
            'admission_year': curriculum.admission_year,
            'basis_of_admission': curriculum.basis_of_admission,
        })

    return JsonResponse(list(curriculums), safe=False)


def create_new_release_from_curriculum(request):
    course_number = int(request.POST.get('course_number'))
    curriculum_id = int(request.POST.get('curriculum_id'))

    curriculum = Curriculum.objects.get(id=curriculum_id)
    study_year_start = curriculum.admission_year + course_number
    study_year_end = curriculum.admission_year + course_number + 1

    study_year = str(study_year_start) + '-' + str(study_year_end)


    release, created = ReleaseFromCurriculum.objects.get_or_create(
        course=course_number,
        curriculum_id=curriculum_id,
        study_year=study_year,
    )

    response = {
        "release_id": release.id,
    }

    return JsonResponse(response, safe=False)


def get_groups_by_curriculum_id(request):
    curriculum_id = request.GET.get('curriculum_id')
    if not curriculum_id or curriculum_id == 'Выберите учебный план':
        return JsonResponse({'error': 'Missing specialty_id'}, status=400)

    response = {}

    curriculum = Curriculum.objects.get(id=curriculum_id)

    basis_of_admission = 'Основное общее'
    if curriculum.basis_of_admission == 11:
        basis_of_admission = 'Среднее общее'


    groups = [ {
        'id': group.id,
        'full_name': group.full_name,
        'students_count': group.students.count(),
    } for group in GroupStudents.objects.filter(
        qualification=curriculum.qualification,
        year_create=curriculum.admission_year,
        education_base=basis_of_admission)]

    response["study_groups"] = groups

    return JsonResponse(response, safe=False)


def get_disciplines_and_teacher_for_theme(request):
    curriculum_id = request.GET.get('curriculum_id')
    release_id = request.GET.get('release_id')
    course = request.GET.get('course')

    response = []
    processed_disciplines = set()

    # 1. Получаем базовые данные по дисциплинам
    clock_cells = ClockCell.objects.filter(
        curriculum=curriculum_id,
        course=course,
        module__isnull=True
    ).select_related('discipline', 'discipline__specialty')

    for clock_cell in clock_cells:
        if not clock_cell.discipline or clock_cell.discipline.id in processed_disciplines:
            continue

        discipline_data = {
            "discipline_id": clock_cell.discipline.id,
            "discipline_name": clock_cell.discipline.name,
            "discipline_code": clock_cell.discipline.code,
            'course_project_cell': '',
            '2pgr_cell': '',
            'cons_cell': '',
            'exam_cell': '',
            'hours_at_week_cell': '',
            'indep_work_cell': '',
            "teachers": get_teachers_groups(curriculum_id, course, clock_cell.discipline.id)
        }

        update_cells(discipline_data, release_id)

        response.append(discipline_data)
        processed_disciplines.add(clock_cell.discipline.id)

    return JsonResponse(response, safe=False)


def get_teachers_groups(curriculum_id, course, discipline_id):
    groups = TeachersForDisciplineAndCurriculum.objects.filter(
        discipline_id=discipline_id,
        course=course,
        curriculum_id=curriculum_id,
    )

    teachers_groups = []

    for group in groups:
        teachers = group.teachers.all()

        for teacher in teachers:
            position = check_teacher_exist(teacher, teachers_groups)

            if position is not None:
                teachers_groups[position].get('groups').add(group.group.id)

            else:
                teachers_groups.append({
                    "teacher_id": teacher.id,
                    "teacher_name": teacher.full_name,
                    "groups": {group.group.id},
                })


    for teacher in teachers_groups:
        teacher['groups'] = list(teacher['groups'])

    return teachers_groups



def update_cells(discipline_data, release_id):
    cells = ReleaseCell.objects.filter(
        release_id=release_id,
        discipline_id=discipline_data.get('discipline_id'),
    )

    for cell in cells:

        match (cell.type_cell):
            case 'кп':
                discipline_data['course_project_cell'] = cell.hours_count

            case 'с/р':
                discipline_data['indep_work_cell'] = cell.hours_count

            case '2п/гр':
                discipline_data['2pgr_cell'] = cell.hours_count

            case 'конс':
                discipline_data['cons_cell'] = cell.hours_count

            case 'экз':
                discipline_data['exam_cell'] = cell.hours_count

            case 'неделя':
                discipline_data['hours_at_week_cell'] = cell.hours_count


def check_teacher_exist(teacher_new, teachers):
    position = None
    for i in range(len(teachers)):
        if teachers[i]['teacher_id'] == teacher_new.id:
            position = i
            break

    return position
