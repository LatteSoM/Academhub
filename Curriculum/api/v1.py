import json
from collections import defaultdict

import pandas as pd
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from lxml.objectify import annotate

from Academhub.models import Specialty, Qualification, Curriculum, GroupStudents, ClockCell, CustomUser

__all__ = (
    'get_study_plans',
    'get_courses_for_study_plan',
    'get_disciplines_by_curriculum_course_term_for_attestation',
    'get_disciplines_by_curriculum_course_term',
    'import_teachers_excel_view',
    'save_teachers_for_groups_and_disciplines',
    'save_periods_for_groups_and_disciplines'
)

from Academhub.models.models import TeachersForDisciplineAndCurriculum, AttestationPeriodForDisciplines


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
    if curriculum.basis_of_admission == 11:
        response["courses"] = [1, 2, 3]
        basis_of_admission = 'Среднее общее'

    else:
        response["courses"] = [1, 2, 3, 4]

    groups = [ {
        'id': group.id,
        'full_name': group.full_name,
        'checked': True
    } for group in GroupStudents.objects.filter(
        qualification=curriculum.qualification,
        year_create=curriculum.admission_year,
        education_base=basis_of_admission)]

    response["study_groups"] = groups

    return JsonResponse(response, safe=False)


@require_POST
def get_disciplines_by_curriculum_course_term_for_attestation(request):
    curriculum_id = request.GET.get('curriculum_id')
    course = int(request.GET.get('course'))
    term = int(request.GET.get('term'))
    checked_groups = json.loads(request.POST.get('checked_groups', '[]'))
    checked_group_ids = {group['id'] for group in checked_groups}  # Множество для быстрого поиска

    response = []
    term_db = semester_dict.get(f'{course}-{term}')
    processed_disciplines = set()

    # Получаем все часы для указанного учебного плана
    clock_cells = ClockCell.objects.filter(
        curriculum=curriculum_id,
        course=course,
        term=term_db,
        module__isnull=True
    ).select_related('discipline', 'discipline__specialty')

    # Получаем все периоды аттестации для выбранных групп одним запросом
    attestation_periods = AttestationPeriodForDisciplines.objects.filter(
        curriculum=curriculum_id,
        course=course,
        term=term_db,
        group_id__in=checked_group_ids
    ).select_related('discipline', 'group')

    # Создаем словарь {discipline_id: {period_data: set(group_ids)}}
    discipline_periods = defaultdict(lambda: defaultdict(set))

    for period in attestation_periods:
        period_key = (period.start_date, period.end_date)
        discipline_periods[period.discipline_id][period_key].add(period.group_id)

    for clock_cell in clock_cells:
        if not clock_cell.discipline or clock_cell.discipline.id in processed_disciplines:
            continue

        discipline_data = {
            "discipline_id": clock_cell.discipline.id,
            "discipline_name": clock_cell.discipline.name,
            "discipline_code": clock_cell.discipline.code,
            "discipline_speciality": clock_cell.discipline.specialty.name if clock_cell.discipline.specialty else '',
            "start_attestation": '',
            "end_attestation": ''
        }

        # Проверяем периоды для текущей дисциплины
        periods_info = discipline_periods.get(clock_cell.discipline.id, {})

        # Ищем период, который содержит ВСЕ выбранные группы
        common_period = None
        for (start_date, end_date), group_ids in periods_info.items():
            if group_ids == checked_group_ids:
                common_period = (start_date, end_date)
                break

        if common_period:
            start_date, end_date = common_period
            discipline_data.update({
                "start_attestation": start_date.strftime('%Y-%m-%d') if start_date else '',
                "end_attestation": end_date.strftime('%Y-%m-%d') if end_date else ''
            })

        response.append(discipline_data)
        processed_disciplines.add(clock_cell.discipline.id)

    return JsonResponse(response, safe=False)

@require_POST
def get_disciplines_by_curriculum_course_term(request):
    curriculum_id = request.POST.get('curriculum_id')
    course = int(request.POST.get('course'))
    term = int(request.POST.get('term'))
    checked_groups = json.loads(request.POST.get('checked_groups', '[]'))
    checked_group_ids = [group['id'] for group in checked_groups]

    response = []
    term_db = semester_dict.get(f'{course}-{term}')
    processed_disciplines = set()

    # 1. Получаем базовые данные по дисциплинам
    clock_cells = ClockCell.objects.filter(
        curriculum=curriculum_id,
        course=course,
        term=term_db,
        module__isnull=True
    ).select_related('discipline', 'discipline__specialty')

    for clock_cell in clock_cells:
        if not clock_cell.discipline or clock_cell.discipline.id in processed_disciplines:
            continue

        discipline_data = {
            "discipline_id": clock_cell.discipline.id,
            "discipline_name": clock_cell.discipline.name,
            "discipline_code": clock_cell.discipline.code,
            "discipline_speciality": clock_cell.discipline.specialty.name if clock_cell.discipline.specialty else '',
            "teachers": []
        }
        response.append(discipline_data)
        processed_disciplines.add(clock_cell.discipline.id)

    # 2. Фильтрация преподавателей по группам (если группы выбраны)
    if checked_group_ids:
        for discipline_data in response:
            # Получаем всех преподавателей для данной дисциплины и групп
            teacher_relations = TeachersForDisciplineAndCurriculum.objects.filter(
                curriculum_id=curriculum_id,
                course=course,
                term=term_db,
                discipline_id=discipline_data['discipline_id'],
                group_id__in=checked_group_ids
            ).prefetch_related('teachers')

            # Собираем словарь {teacher_id: количество групп, в которых он встречается}
            teacher_group_counts = {}

            for relation in teacher_relations:
                for teacher in relation.teachers.all():
                    if teacher.id not in teacher_group_counts:
                        teacher_group_counts[teacher.id] = 0
                    teacher_group_counts[teacher.id] += 1

            # Отбираем только тех преподавателей, которые есть во всех группах
            common_teachers = [
                teacher_id for teacher_id, count in teacher_group_counts.items()
                if count == len(checked_group_ids)
            ]

            # Получаем полные данные о преподавателях
            if common_teachers:
                teachers = CustomUser.objects.filter(id__in=common_teachers).select_related('speciality')
                discipline_data['teachers'] = [
                    {
                        "teacher_id": teacher.id,
                        "full_name": teacher.full_name,
                        "cmc": teacher.cmc,
                        "speciality": teacher.speciality.name if teacher.speciality else '',
                    }
                    for teacher in teachers
                ]


    return JsonResponse(response, safe=False)




def import_teachers_excel_view(request):
    response = {}
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            response['message'] = "Не был выбран файл Excel."
            return JsonResponse(response, safe=False)

        if not excel_file.name.endswith(('.xls', '.xlsx')):
             response['message'] = "Неверный формат файла. Пожалуйста, загрузите файл Excel (.xls или .xlsx)."
             return JsonResponse(response, safe=False)

        created_count = 0
        updated_count = 0
        found_count = 0
        skipped_count = 0
        deactivated_count = 0
        errors = []
        excel_emails = set()

        try:
            df = pd.read_excel(excel_file, sheet_name=0)
            required_columns = ['ФИО','email', 'ЦМК', 'специализация']

            if not all(col in df.columns for col in required_columns):
                missing_cols = [col for col in required_columns if col not in df.columns]
                response['message'] = f"В файле отсутствуют необходимые столбцы: {', '.join(missing_cols)}"
                return JsonResponse(response, safe=False)

            teachers_list = []
            for index, row in df.iterrows():
                try:
                    full_name_raw = row.get('ФИО')
                    email_raw = row.get('email')
                    cmk_raw = row.get('ЦМК')
                    specialty_raw = row.get('специализация')

                    full_name = str(full_name_raw).strip() if pd.notna(full_name_raw) else None
                    email = str(email_raw).strip() if pd.notna(email_raw) else None
                    cmc = str(cmk_raw).strip() if pd.notna(cmk_raw) else None
                    specialty = str(specialty_raw).strip() if pd.notna(specialty_raw) else None

                    if not all([full_name, email]):
                        errors.append(f"Строка {index + 2}: Отсутствуют обязательные данные (ФИО или email).")
                        skipped_count += 1
                        continue

                    name_parts = full_name.split()
                    last_name = name_parts[0] if len(name_parts) > 0 else ''
                    first_name = name_parts[1] if len(name_parts) > 1 else ''
                    # middle_name = ' '.join(name_parts[2:]) if len(name_parts) > 2 else '' # Not used currently based on user edits

                    if not last_name or not first_name:
                         errors.append(f"Строка {index + 2}: Не удалось разобрать ФИО '{full_name}'. Ожидается как минимум Фамилия и Имя.")
                         skipped_count += 1
                         continue

                    user_defaults = {
                        'full_name': full_name,
                        'is_teacher': True,
                    }

                    speciality_name, code = specialty.split('_')

                    specialty_obj, created = Specialty.objects.get_or_create(
                        name=speciality_name,
                        code=code,
                    )


                    filter_user = CustomUser.objects.filter(
                        email=email,
                        full_name=full_name,
                        is_teacher=True,
                    )

                    if len(filter_user) == 0:
                        user, created = CustomUser.objects.update_or_create(
                            email=email,
                            defaults=user_defaults,
                            cmc=cmc,
                            speciality=specialty_obj
                        )

                        teachers_list.append({
                            'teacher_id': user.id,
                            'full_name': user.full_name,
                            'cmc': user.cmc,
                            'speciality': user.speciality.name,
                        })
                        if created:
                            email_part = str(email.split("@")[0])
                            against_overkill_par = "123456789"
                            user.set_password(email_part + against_overkill_par)
                            user.speciality = specialty_obj
                            user.is_active = True
                            user.save()
                            created_count += 1
                        else:
                            updated_count += 1

                    else:
                        found_count += 1

                        if filter_user[0].speciality is not None:
                            teachers_list.append({
                                'teacher_id': filter_user[0].id,
                                'full_name': filter_user[0].full_name,
                                'cmc': filter_user[0].cmc,
                                'speciality': filter_user[0].speciality.name,
                            })

                        else:
                            teachers_list.append({
                                'teacher_id': filter_user[0].id,
                                'full_name': filter_user[0].full_name,
                                'cmc': filter_user[0].cmc,
                                'speciality': "",
                            })


                    excel_emails.add(email)

                except Exception as e:
                    errors.append(f"Строка {index + 2}: Ошибка обработки - {e}")
                    skipped_count += 1

            existing_teacher_emails = set(CustomUser.objects.filter(is_teacher=True, is_active=True).values_list('email', flat=True))
            emails_to_deactivate = existing_teacher_emails - excel_emails

            if emails_to_deactivate:
                users_to_deactivate = CustomUser.objects.filter(email__in=emails_to_deactivate, is_teacher=True)
                for user in users_to_deactivate:
                    user.is_active = False
                    user.save()
                    deactivated_count += 1

        except Exception as e:
            response['message'] = f"Произошла ошибка при обработке файла: {e}"
            return JsonResponse(response, safe=False)

        final_message_parts = []
        if created_count > 0:
            final_message_parts.append(f"Создано: {created_count}")
        if updated_count > 0:
            final_message_parts.append(f"Обновлено/Подтверждено: {updated_count}")
        if deactivated_count > 0:
            final_message_parts.append(f"Деактивировано (не найдены в файле): {deactivated_count}")
        if skipped_count > 0:
            final_message_parts.append(f"Пропущено строк из-за ошибок: {skipped_count}")
        if found_count > 0:
            final_message_parts.append(f"Найдено преподавателей: {found_count}")

        if final_message_parts:
             final_message = "Импорт завершен. " + ", ".join(final_message_parts) + "."
             if created_count > 0 or updated_count > 0 or deactivated_count > 0:
                 response['message'] = final_message
                 response['teachers'] = teachers_list
                 return JsonResponse(response, safe=False)
             else:
                 response['message'] = final_message
                 response['teachers'] = teachers_list
                 return JsonResponse(response, safe=False)
        else:
            response['message'] = "Файл обработан, но не найдено данных для создания, обновления или деактивации."
            return JsonResponse(response, safe=False)

    else:
        response['message'] = "Недопустимый метод запроса."
        return JsonResponse(response, safe=False)


def save_teachers_for_groups_and_disciplines(request):
    response = {}
    if request.method == 'POST':
        try:
            with transaction.atomic():  # Используем транзакцию для целостности данных
                # Получаем базовые параметры
                curriculum_id = request.POST.get('curriculum_id')
                course = request.POST.get('course')
                term = request.POST.get('term')
                disciplines_with_teachers = json.loads(request.POST.get('disciplines_with_teachers', '[]'))
                checked_groups = json.loads(request.POST.get('checked_groups', '[]'))

                # Получаем выбранные группы
                selected_group_ids = [str(group['id']) for group in checked_groups if group.get('checked')]
                groups = GroupStudents.objects.filter(id__in=selected_group_ids)

                for group in groups:
                    # Обрабатываем каждую дисциплину
                    for discipline_data in disciplines_with_teachers:
                        # Получаем или создаем базовую запись
                        term_db = semester_dict.get(f"{course}-{term}")
                        obj, created = TeachersForDisciplineAndCurriculum.objects.get_or_create(
                            curriculum_id=curriculum_id,
                            course=course,
                            term=term_db,
                            discipline_id=discipline_data['discipline_id'],
                            group_id=group.id,
                            defaults={
                                'curriculum_id': curriculum_id,
                                'course': course,
                                'term': term_db,
                                'discipline_id': discipline_data['discipline_id'],
                                'group_id': group.id,
                            }
                        )

                        # Обновляем преподавателей
                        teacher_ids = [str(t['teacher_id']) for t in discipline_data['teachers']]
                        obj.teachers.set(CustomUser.objects.filter(id__in=teacher_ids))

                        # Удаляем записи которых нет в полученных данных
                        # existing_discipline_ids = [d['discipline_id'] for d in disciplines_with_teachers]
                        # TeachersForDisciplineAndCurriculum.objects.filter(
                        #     curriculum_id=curriculum_id,
                        #     course=course,
                        #     term=term
                        # ).exclude(discipline_id__in=existing_discipline_ids).delete()

                response['status'] = 'success'
                response['message'] = 'Данные успешно сохранены'

        except Exception as e:
            response['status'] = 'error'
            response['message'] = f'Ошибка: {str(e)}'

    return JsonResponse(response)


def save_periods_for_groups_and_disciplines(request):
    response = {}
    if request.method == 'POST':
        try:
            with transaction.atomic():  # Используем транзакцию для целостности данных
                # Получаем базовые параметры
                curriculum_id = request.POST.get('curriculum_id')
                course = request.POST.get('course')
                term = request.POST.get('term')
                disciplines_with_periods = json.loads(request.POST.get('disciplines_with_periods', '[]'))
                checked_groups = json.loads(request.POST.get('checked_groups', '[]'))

                # Получаем выбранные группы
                selected_group_ids = [str(group['id']) for group in checked_groups ]
                groups = GroupStudents.objects.filter(id__in=selected_group_ids)

                # Обрабатываем каждую дисциплину
                for group in groups:
                    for discipline_data in disciplines_with_periods:
                        if discipline_data['start_attestation'] != "" and discipline_data['end_attestation'] != "":
                            # Получаем или создаем базовую запись
                            term_db = semester_dict.get(f"{course}-{term}")
                            obj, created = AttestationPeriodForDisciplines.objects.get_or_create(
                                curriculum_id=curriculum_id,
                                course=course,
                                term=term_db,
                                discipline_id=discipline_data['discipline_id'],
                                group_id=group.id,
                                defaults={
                                    'curriculum_id': curriculum_id,
                                    'course': course,
                                    'term': term_db,
                                    'discipline_id': discipline_data['discipline_id'],
                                    'start_date': discipline_data['start_attestation'],
                                    'end_date': discipline_data['end_attestation'],
                                    'group_id': group.id,
                                }
                            )

                response['status'] = 'success'
                response['message'] = 'Данные успешно сохранены'

        except Exception as e:
            response['status'] = 'error'
            response['message'] = f'Ошибка: {str(e)}'

    return JsonResponse(response)




