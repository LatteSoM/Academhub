

from django.apps import AppConfig




class AcademhubAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Academhub"

    def ready(self, daily_task=None):
        # Импортируем модель здесь, внутри метода ready()
        from Academhub.models import GroupStudents
        from django.db import connection
        import threading
        import time
        from Academhub.models import Discipline, GradebookStudents
        from Academhub.models import Curriculum
        from Academhub.models import Gradebook
        from Academhub.models import CurriculumItem
        from Academhub.models import Student
        from Academhub.models import PracticeDate
        from Academhub.models import ProfessionalModule

        from Academhub.models import TermPaper

        from Academhub.models import Practice


        def check_student_eligibility(student, code, current_semester):
            """
                Проверяет, имеет ли студент допуск по всем связанным дисциплинам
            """
            # 1. Получить все оценки студента по целевым дисциплинам
            grades = GradebookStudents.objects.filter(
                student=student,
                gradebook__discipline__code=code,
                gradebook__semester_number=current_semester,
                gradebook__status="Заполнена"
            ).exclude(grade__in=['Неявка', 'Неудовлетворительно', ''])

            # 2. Получить все уникальные дисциплины по которым есть оценки
            graded_disciplines = set(grades.values_list('gradebook__discipline', flat=True))

            # 3. Получить все целевые дисциплины
            target_disciplines = Discipline.objects.filter(code=code)

            # 4. Проверить что все дисциплины покрыты
            return len(target_disciplines) - 1 == len(graded_disciplines)


        def create_gradebooks_for_session(semester_number_of_grade_book, calendar):
            """
                Функция для генерации ведомостей под семестровую аттестацию
            """
            learning_plan = Curriculum.objects.filter(qualification=calendar.group.qualification,
                                                      admission_year=calendar.group.year_create)
            learning_plan_disciplines = CurriculumItem.objects.filter(
                curriculum=learning_plan[0],  # Фильтр по учебному плану
                item_type__in=['discipline', 'term_paper']  # Фильтр по типу
            )

            for learning_plan_discipline in learning_plan_disciplines:

                grade_book = Gradebook()
                grade_book.status = Gradebook.STATUS_CHOICE[0][0]

                grade_book.semester_number = semester_number_of_grade_book

                grade_book.group = calendar.group

                students = Student.objects.filter(
                    group=calendar.group,  # Фильтр по группе
                    is_expelled=False,  # Студент не отчислен
                    is_in_academ=False  # Студент не в академе
                )

                if learning_plan_discipline.semester == grade_book.semester_number:
                    if learning_plan_discipline.item_type == "term_paper":
                        grade_book.discipline = learning_plan_discipline.term_paper.discipline
                        print(learning_plan_discipline.term_paper.discipline, " ", learning_plan_discipline.attestation_form)
                    else:
                        grade_book.discipline = learning_plan_discipline.discipline
                        print(learning_plan_discipline.discipline, " ", learning_plan_discipline.attestation_form)
                else:
                    continue

                if Gradebook.objects.filter(group=calendar.group,
                                            discipline=grade_book.discipline_id,
                                            semester_number=grade_book.semester_number).exists():
                    print(
                        f"⚠️ Ведомость для {calendar.group} по {grade_book.discipline} уже существует, пропускаем!")
                    continue  # Пропускаем создание дубликата

                if learning_plan_discipline.attestation_form == "exam":
                    grade_book.name = "Экзаменационная ведомость"
                elif learning_plan_discipline.attestation_form == "credit":
                    grade_book.name = "Ведомость дифференцированного зачета"
                elif learning_plan_discipline.attestation_form == "none":
                    grade_book.name = "Ведомость успеваемости"
                elif learning_plan_discipline.attestation_form == "course_pr":
                    grade_book.name = "Ведомость защиты курсового проекта"

                grade_book.save()
                grade_book.students.add(*students)

        def create_grade_books_for_pm(semester_number_of_grade_book, calendar):
            """
                Функция для генерации ведомостей для Профессионального модуля
            """
            learning_plan = Curriculum.objects.filter(qualification=calendar.group.qualification,
                                                      admission_year=calendar.group.year_create)
            learning_plan_disciplines = CurriculumItem.objects.filter(curriculum=learning_plan[0], item_type="professional_module")

            for learning_plan_discipline in learning_plan_disciplines:
                print(learning_plan_discipline.professional_module.discipline, " ", learning_plan_discipline.attestation_form)
                grade_book = Gradebook()
                grade_book.status = Gradebook.STATUS_CHOICE[0][0]

                grade_book.semester_number = semester_number_of_grade_book

                grade_book.group = calendar.group

                all_students = Student.objects.filter(
                    group=calendar.group,  # Фильтр по группе
                    is_expelled=False,     # Студент не отчислен
                    is_in_academ=False     # Студент не в академе
                )
                students = []
                for student in all_students:
                    if check_student_eligibility(student, learning_plan_discipline.professional_module.discipline.code, grade_book.semester_number):
                        students.append(student)

                grade_book.discipline = learning_plan_discipline.professional_module.discipline

                if Gradebook.objects.filter(group=calendar.group,
                                            discipline=grade_book.discipline_id,
                                            semester_number=grade_book.semester_number).exists():
                    print(
                        f"⚠️ Ведомость для {calendar.group} по {grade_book.discipline} уже существует, пропускаем!")
                    continue  # Пропускаем создание дубликата

                grade_book.name = "Экзаменационная ведомость"
                grade_book.save()
                grade_book.students.add(*students)

        def generate_gradebooks_for_practices(practice):
            print(practice.curriculum_item.practice.practice_name, " ", practice.curriculum_item.attestation_form)
            grade_book = Gradebook()
            grade_book.status = Gradebook.STATUS_CHOICE[0][0]

            grade_book.semester_number = practice.curriculum_item.semester

            grade_book.group = practice.calendar_graphic.group

            students = Student.objects.filter(
                group=grade_book.group,  # Фильтр по группе
                is_expelled=False,  # Студент не отчислен
                is_in_academ=False  # Студент не в академе
            )

            grade_book.discipline = practice.curriculum_item.practice.discipline

            if Gradebook.objects.filter(group=grade_book.group,
                                        discipline=grade_book.discipline_id,
                                        semester_number=grade_book.semester_number).exists():
                print(
                    f"⚠️ Ведомость для {grade_book.group} по {grade_book.discipline} уже существует, пропускаем!")
            else:
                grade_book.name = "Ведомость дифференцированного зачета"
                grade_book.save()
                grade_book.students.add(*students)


        def daily_task():
            semester_number_of_grade_book = 0
            print(f"⏳ Поток daily_task запущен! Активные потоки: {[t.name for t in threading.enumerate()]}")
            from Academhub.models import CalendarGraphicOfLearningProcess
            from django.utils.timezone import localtime
            from django.utils.timezone import activate
            import pytz


            while True:
                activate(pytz.timezone("Europe/Moscow"))  # Устанавливаем Москву
                today = localtime().date()
                calendar_graphic = CalendarGraphicOfLearningProcess.objects.all()
                for calendar in calendar_graphic:

                    # берем все практики текущего календарного графика
                    all_practices_with_dates = PracticeDate.objects.filter(calendar_graphic=calendar)
                    for practice in all_practices_with_dates:
                        if today == practice.start_date:
                            generate_gradebooks_for_practices(practice)
                    flag = False

                    if today == calendar.start_exam_date_first_semester:
                        semester_number_of_grade_book = (calendar.group.current_course - 1) * 2 + 1
                        create_gradebooks_for_session(semester_number_of_grade_book, calendar)
                        flag = True

                    if today == calendar.start_exam_date_second_semester:
                        semester_number_of_grade_book = calendar.group.current_course * 2
                        create_gradebooks_for_session(semester_number_of_grade_book, calendar)
                        flag = True

                    if today == calendar.date_of_pm_first_semester:
                        semester_number_of_grade_book = (calendar.group.current_course - 1) * 2 + 1
                        create_grade_books_for_pm(semester_number_of_grade_book, calendar)
                        flag = True

                    if today == calendar.date_of_pm_second_semester:
                        semester_number_of_grade_book = calendar.group.current_course * 2
                        create_grade_books_for_pm(semester_number_of_grade_book, calendar)
                        flag = True

                    if not flag:
                        continue



                time.sleep(86400)  # Запуск раз в день

        if not any(thread.name == "daily_task" for thread in threading.enumerate()):
            thread = threading.Thread(target=daily_task, name="daily_task", daemon=True)
            thread.start()
