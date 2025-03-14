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

        def check_student_eligibility(student, code, current_semester):
            """
                Проверяет, имеет ли студент допуск по всем связанным дисциплинам
            """
            # 1. Получить все оценки студента по целевым дисциплинам
            grades = GradebookStudents.objects.filter(
                student=student,
                gradebook__discipline__code=code,
                gradebook__semester_number=current_semester
            ).exclude(grade__in=['Неявка', '2', ''])

            # 2. Получить все уникальные дисциплины по которым есть оценки
            graded_disciplines = set(grades.values_list('gradebook__discipline', flat=True))

            # 3. Получить все целевые дисциплины
            target_disciplines = Discipline.objects.filter(code=code)

            # 4. Проверить что все дисциплины покрыты
            return target_disciplines.count() - 1 == graded_disciplines.count()

        def daily_task():
            semester_number_of_grade_book = 0
            print(f"⏳ Поток daily_task запущен! Активные потоки: {[t.name for t in threading.enumerate()]}")
            from Academhub.models import CalendarGraphicOfLearningProcess
            from django.utils.timezone import localtime
            from django.utils.timezone import activate
            import pytz
            from datetime import timedelta
            from Academhub.models import Curriculum
            from Academhub.models import Gradebook
            from Academhub.models import CurriculumItem
            from Academhub.models import Student
            from Academhub.models import ProfessionalModule

            from Academhub.models import TermPaper

            from Academhub.models import Practice

            while True:
                activate(pytz.timezone("Europe/Moscow"))  # Устанавливаем Москву
                today = localtime().date()
                grade_book_counter = 1
                calendar_graphic = CalendarGraphicOfLearningProcess.objects.all()
                for calendar in calendar_graphic:

                    if today == calendar.start_exam_date_first_semester - timedelta(days=2):
                        semester_number_of_grade_book = (calendar.group.current_course - 1) * 2 + 1
                        grade_for_pm = False

                    elif today == calendar.start_exam_date_second_semester - timedelta(days=2):
                        # TODO: Назаначение номера семестра для ведомости
                        print("Ура, сегодня дата начала сессии второго семестра")
                        grade_for_pm = False
                    elif today == calendar.date_of_pm_first_semester - timedelta(days=1) or today == calendar.date_of_pm_second_semester - timedelta(days=1):
                        grade_for_pm = True
                    else:
                        continue

                    learning_plan = Curriculum.objects.filter(qualification=calendar.group.qualification,
                                                              admission_year=calendar.group.year_create)
                    learning_plan_disciplines = CurriculumItem.objects.filter(curriculum=learning_plan[0])

                    for learning_plan_discipline in learning_plan_disciplines:

                        print(learning_plan_discipline.discipline, " ", learning_plan_discipline.attestation_form)
                        grade_book = Gradebook()
                        grade_book.status = Gradebook.STATUS_CHOICE[0][0]

                        grade_book.semester_number = semester_number_of_grade_book

                        grade_book.group = calendar.group

                        if not grade_for_pm:
                            students = Student.objects.filter(group=calendar.group)
                        else:

                            all_students = Student.objects.filter(group=calendar.group)
                            students = []
                            for student in all_students:
                                if check_student_eligibility(student, learning_plan_discipline.discipline.code, grade_book.semester_number):
                                    students.append(student)


                        if learning_plan_discipline.semester == grade_book.semester_number:
                            if learning_plan_discipline.item_type == "professional_module" and not grade_for_pm:
                                continue
                            if learning_plan_discipline.item_type == "professional_module" and grade_for_pm:
                                prof_module = ProfessionalModule.objects.filter(
                                    discipline=learning_plan_discipline.professional_module.discipline)
                                grade_book.discipline = prof_module[0].discipline
                            elif learning_plan_discipline.item_type == "term_paper":
                                grade_book.discipline = TermPaper.objects.filter(
                                    discipline=learning_plan_discipline.discipline) # TODO: Правильно передать дисциплину
                            elif learning_plan_discipline.item_type == "practice":
                                practice = Practice.objects.filter(
                                    discipline=learning_plan_discipline.practice.discipline)
                                grade_book.discipline = practice[0].discipline
                            else:
                                grade_book.discipline = learning_plan_discipline.discipline
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
                        elif learning_plan_discipline.attestation_form == "learning_practice":
                            grade_book.name = "Ведомость учебной практики"
                        elif learning_plan_discipline.attestation_form == "profession_practice":
                            grade_book.name = "Ведомость производственной практики"
                        elif learning_plan_discipline.attestation_form == "course_pr":
                            grade_book.name = "Ведомость защиты курсового проекта"



                        grade_book.number = "18.01-" + str(today.year)[-2:] + "/" + str(grade_book_counter)
                        grade_book.save()
                        grade_book.students.add(*students)
                        grade_book_counter += 1

                time.sleep(86400)  # Запуск раз в день

        if not any(thread.name == "daily_task" for thread in threading.enumerate()):
            thread = threading.Thread(target=daily_task, name="daily_task", daemon=True)
            thread.start()
