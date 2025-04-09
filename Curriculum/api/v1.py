from enum import unique

from django.http import JsonResponse
from Academhub.models import Specialty, Qualification, Curriculum, GroupStudents, ClockCell

__all__ = (
    'get_study_plans',
    'get_courses_for_study_plan',
    'get_disciplines_by_curriculum_course_term',
)


def get_study_plans(request):
    specialty_id = request.GET.get('specialty_id')
    if not specialty_id or specialty_id == 'Выберите специальность':
        return JsonResponse({'error': 'Missing specialty_id'}, status=400)

    specialty = Specialty.objects.get(id=specialty_id)
    qualifications = Qualification.objects.filter(specialty=specialty)

    curriculums = []
    for qualification in qualifications:

        for curriculum in qualification.curriculums.all():
            curriculums.append({
                "id": curriculum.id,
                "qualification_name": curriculum.qualification_name,
                'admission_year': curriculum.admission_year,
                'basis_of_admission': curriculum.basis_of_admission,
            })

    return JsonResponse(list(curriculums), safe=False)


def get_courses_for_study_plan(request):
    curriculum_id = request.GET.get('curriculum_id')
    if not curriculum_id or curriculum_id == 'Выберите учебный план':
        return JsonResponse({'error': 'Missing specialty_id'}, status=400)

    response = {}

    curriculum = Curriculum.objects.get(id=curriculum_id)
    basis_of_admission = 'Основное общее'
    if curriculum.admission_year == 11:
        response["courses"] = [1, 2, 3]
        basis_of_admission = 'Среднее общее'

    else:
        response["courses"] = [1, 2, 3, 4]

    groups = [ {
        'id': group.id,
        'full_name': group.full_name
    } for group in GroupStudents.objects.filter(
        qualification=curriculum.qualification,
        year_create=curriculum.admission_year,
        education_base=basis_of_admission)]

    response["study_groups"] = groups

    return JsonResponse(response, safe=False)


def get_disciplines_by_curriculum_course_term(request):
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

    curriculum_id = request.GET.get('curriculum_id')
    course = int(request.GET.get('course'))
    term = int(request.GET.get('term'))

    unique_disciplines: set = set()
    response = []

    term_db = semester_dict.get(f'{course}-{term}')
    for clock_cell in  ClockCell.objects.filter(curriculum=curriculum_id, course=course, term=term_db, module__isnull=True):
        if clock_cell.discipline is not None:
            if clock_cell.discipline.name not in unique_disciplines:
                unique_disciplines.add(clock_cell.discipline.name)

                response.append({
                    "discipline_id": clock_cell.discipline.id,
                    'discipline_name': clock_cell.discipline.name,
                    'discipline_code': clock_cell.discipline.code
                })

    return JsonResponse(response, safe=False)



