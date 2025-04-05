from django.http import JsonResponse
from Academhub.models import Specialty, Qualification, Curriculum, GroupStudents

__all__ = (
    'get_study_plans',
    'get_courses_for_study_plan',
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
