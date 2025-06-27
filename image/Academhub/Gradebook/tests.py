from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from Academhub.models import (
    CustomUser, Gradebook, Student, GradebookStudents, Curriculum, ClockCell, Discipline,
    GroupStudents, TeachersForDisciplineAndCurriculum, Specialty, Qualification
)
from .views import (
    perform_generation,
    check_and_open_gradebook, download_report, fetch_group_semester_attestation_table, export_diplom_types
)
from .filters import GradebookFilter

class GradebookTests(TestCase):
    def setUp(self):
        # Создаём специальность и квалификацию
        self.specialty = Specialty.objects.create(code="09.02.07", name="Информационные системы")
        self.qualification = Qualification.objects.create(
            short_name="ИС", name="Программист", specialty=self.specialty
        )
        # Создаём группу
        self.group = GroupStudents.objects.create(
            qualification=self.qualification, number=1, education_base="Основное общее",
            year_create=2023, current_course=1
        )
        # Создаём дисциплину
        self.discipline = Discipline.objects.create(
            code="ТД.01", name="Тестовая дисциплина", specialty=self.specialty
        )
        # Создаём пользователя для тестов
        self.user = CustomUser.objects.create(email="user@example.com", full_name="Тестовый Пользователь")

    # def test_update_gradebooks_after_deactivation_removes_teachers(self):
    #     teacher = CustomUser.objects.create(email="teacher@example.com", is_active=True)
    #     gradebook = Gradebook.objects.create(
    #         status="Открыта", name="Test Gradebook", semester_number=1, group=self.group,
    #         discipline=self.discipline, number="18.01-23/0001"
    #     )
    #     gradebook.teachers.add(teacher)
    #     teacher.is_active = False
    #     teacher.save()
    #     deactivated_teachers = CustomUser.objects.filter(is_active=False)
    #     update_gradebooks_after_deactivation(deactivated_teachers)
    #     gradebook.refresh_from_db()
    #     self.assertFalse(gradebook.teachers.filter(id=teacher.id).exists())
    #     self.assertEqual(gradebook.status, "Не заполнена")

    # def test_update_gradebooks_after_deactivation_no_teachers(self):
    #     gradebook = Gradebook.objects.create(
    #         status="Открыта", name="Test Gradebook", semester_number=1, group=self.group,
    #         discipline=self.discipline, number="18.01-23/0002"
    #     )
    #     deactivated_teachers = CustomUser.objects.filter(is_active=False)
    #     update_gradebooks_after_deactivation(deactivated_teachers)
    #     gradebook.refresh_from_db()
    #     self.assertEqual(gradebook.status, "Открыта")
    #
    # def test_update_gradebooks_after_deactivation_closed_gradebook(self):
    #     teacher = CustomUser.objects.create(email="teacher@example.com", is_active=True)
    #     gradebook = Gradebook.objects.create(
    #         status="Закрыта", name="Test Gradebook", semester_number=1, group=self.group,
    #         discipline=self.discipline, number="18.01-23/0003"
    #     )
    #     gradebook.teachers.add(teacher)
    #     teacher.is_active = False
    #     teacher.save()
    #     deactivated_teachers = CustomUser.objects.filter(is_active=False)
    #     update_gradebooks_after_deactivation(deactivated_teachers)
    #     gradebook.refresh_from_db()
    #     self.assertTrue(gradebook.teachers.filter(id=teacher.id).exists())
    #     self.assertEqual(gradebook.status, "Закрыта")

    def test_perform_generation_primary_success(self):
        curriculum = Curriculum.objects.create(
            qualification=self.qualification, admission_year=2023, basis_of_admission=9
        )
        clock_cell = ClockCell.objects.create(
            curriculum=curriculum, term=1, discipline=self.discipline, code_of_type_work="Экзамен",
            course=1, count_of_clocks=36
        )
        result = perform_generation(semester_number=1, grade_book_type="Первичная сдача")
        self.assertEqual(result["generated"], 1)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["errors"], 0)
        gradebook = Gradebook.objects.first()
        self.assertEqual(gradebook.name, "Экзаменационная ведомость")
        self.assertEqual(gradebook.status, "Не заполнена")

    def test_perform_generation_resit_no_students(self):
        curriculum = Curriculum.objects.create(
            qualification=self.qualification, admission_year=2023, basis_of_admission=9
        )
        clock_cell = ClockCell.objects.create(
            curriculum=curriculum, term=1, discipline=self.discipline, code_of_type_work="Экзамен",
            course=1, count_of_clocks=36
        )
        primary_gradebook = Gradebook.objects.create(
            discipline=self.discipline, group=self.group, semester_number=1,
            type_of_grade_book="Первичная сдача", status="Закрыта", number="18.01-23/0004"
        )
        result = perform_generation(semester_number=1, grade_book_type="Пересдача")
        self.assertEqual(result["generated"], 0)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(Gradebook.objects.count(), 1)

    def test_perform_generation_invalid_semester(self):
        result = perform_generation(semester_number=0, grade_book_type="Первичная сдача")
        self.assertEqual(result["generated"], 0)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(Gradebook.objects.count(), 0)

    # def test_update_grade_book_contingent_success(self):
    #     gradebook = Gradebook.objects.create(
    #         status="Не заполнена", semester_number=1, group=self.group, discipline=self.discipline,
    #         number="18.01-23/0005"
    #     )
    #     student = Student.objects.create(
    #         full_name="Иванов И.И.", group=self.group, phone="1234567890", birth_date="2000-01-01",
    #         snils="123-456-789 00", admission_order="Приказ 1", registration_address="Адрес 1",
    #         actual_address="Адрес 2", representative_full_name="Петров П.П.",
    #         representative_email="parent@example.com"
    #     )
    #     teacher = CustomUser.objects.create(email="teacher@example.com", full_name="Препод Тест")
    #     teacher_link = TeachersForDisciplineAndCurriculum.objects.create(
    #         discipline=self.discipline, group=self.group, term=1, curriculum=self.group.curriculum,
    #         course=1
    #     )
    #     teacher_link.teachers.add(teacher)
    #     success = update_grade_book_contingent(gradebook, [student])
    #     self.assertTrue(success)
    #     gradebook.refresh_from_db()
    #     self.assertEqual(gradebook.teachers.count(), 1)
    #     self.assertEqual(GradebookStudents.objects.count(), 1)
    #     self.assertEqual(gradebook.status, "Не заполнена")

    # def test_update_grade_book_contingent_pm_discipline(self):
    #     discipline = Discipline.objects.create(
    #         name="ПМ.01.Test", code="ПМ.01.ЭК", specialty=self.specialty
    #     )
    #     gradebook = Gradebook.objects.create(
    #         status="Не заполнена", semester_number=1, group=self.group, discipline=discipline,
    #         number="18.01-23/0006"
    #     )
    #     student = Student.objects.create(
    #         full_name="Иванов И.И.", group=self.group, phone="1234567890", birth_date="2000-01-01",
    #         snils="123-456-789 00", admission_order="Приказ 1", registration_address="Адрес 1",
    #         actual_address="Адрес 2", representative_full_name="Петров П.П.",
    #         representative_email="parent@example.com"
    #     )
    #     success = update_grade_book_contingent(gradebook, [student])
    #     self.assertTrue(success)
    #     self.assertEqual(GradebookStudents.objects.count(), 0)  # Студент не добавлен для ПМ

    def test_gradebook_filter_by_group(self):
        gradebook = Gradebook.objects.create(
            status="Открыта", semester_number=1, group=self.group, discipline=self.discipline,
            number="18.01-23/0007"
        )
        filter_data = {"group": self.group.id}
        gradebook_filter = GradebookFilter(filter_data, queryset=Gradebook.objects.all())
        result = gradebook_filter.qs
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), gradebook)

    def test_check_and_open_gradebook_success(self):
        teacher = CustomUser.objects.create(email="teacher@example.com", full_name="Препод Тест")
        student = Student.objects.create(
            full_name="Иванов И.И.", group=self.group, phone="1234567890", birth_date="2000-01-01",
            snils="123-456-789 00", admission_order="Приказ 1", registration_address="Адрес 1",
            actual_address="Адрес 2", representative_full_name="Петров П.П.",
            representative_email="parent@example.com"
        )
        gradebook = Gradebook.objects.create(
            name="Test Gradebook", status="Не заполнена", semester_number=1, group=self.group,
            discipline=self.discipline, number="18.01-23/0008"
        )
        gradebook.teachers.add(teacher)
        GradebookStudents.objects.create(student=student, gradebook=gradebook, grade="-")
        request = self.client.get(reverse("check_open_gradebook", kwargs={"pk": gradebook.id}))
        response = check_and_open_gradebook(request, pk=gradebook.id)
        gradebook.refresh_from_db()
        self.assertEqual(gradebook.status, "Открыта")
        self.assertIsNotNone(gradebook.date_of_opening)

    def test_download_report_closes_gradebook(self):
        teacher = CustomUser.objects.create(email="teacher@example.com", full_name="Препод Тест")
        student = Student.objects.create(
            full_name="Иванов И.И.", group=self.group, phone="1234567890", birth_date="2000-01-01",
            snils="123-456-789 00", admission_order="Приказ 1", registration_address="Адрес 1",
            actual_address="Адрес 2", representative_full_name="Петров П.П.",
            representative_email="parent@example.com"
        )
        gradebook = Gradebook.objects.create(
            name="Test Gradebook", status="Заполнена", semester_number=1, group=self.group,
            discipline=self.discipline, number="18.01-23/0009"
        )
        gradebook.teachers.add(teacher)
        GradebookStudents.objects.create(student=student, gradebook=gradebook, grade="5")
        request = self.client.get(reverse("download_report", kwargs={"pk": gradebook.id}))
        request.user = self.user
        response = download_report(request, pk=gradebook.id)
        gradebook.refresh_from_db()
        self.assertEqual(gradebook.status, "Закрыта")
        self.assertIsNotNone(gradebook.date_of_closing)

    def test_fetch_group_semester_attestation_table_quality_percentage(self):
        curriculum = Curriculum.objects.create(
            qualification=self.qualification, admission_year=2023, basis_of_admission=9
        )
        clock_cell = ClockCell.objects.create(
            curriculum=curriculum, term=1, discipline=self.discipline, code_of_type_work="Экзамен",
            course=1, count_of_clocks=36
        )
        student = Student.objects.create(
            full_name="Иванов И.И.", group=self.group, phone="1234567890", birth_date="2000-01-01",
            snils="123-456-789 00", admission_order="Приказ 1", registration_address="Адрес 1",
            actual_address="Адрес 2", representative_full_name="Петров П.П.",
            representative_email="parent@example.com", is_expelled=False, is_in_academ=False
        )
        gradebook = Gradebook.objects.create(
            semester_number=1, group=self.group, discipline=self.discipline, status="Закрыта",
            number="18.01-23/0010", date_of_closing=timezone.now()
        )
        GradebookStudents.objects.create(student=student, gradebook=gradebook, grade="5")
        data = fetch_group_semester_attestation_table(semester=1, group=self.group)
        self.assertEqual(data["quality_percentages"][self.discipline.id], 100.0)
        self.assertEqual(data["total_quality_percentage"], 100.0)

    def test_export_diplom_types_red_diploma(self):
        student = Student.objects.create(
            full_name="Иванов И.И.", group=self.group, phone="1234567890", birth_date="2000-01-01",
            snils="123-456-789 00", admission_order="Приказ 1", registration_address="Адрес 1",
            actual_address="Адрес 2", representative_full_name="Петров П.П.",
            representative_email="parent@example.com", is_expelled=False, is_in_academ=False
        )
        gradebook = Gradebook.objects.create(
            semester_number=1, group=self.group, discipline=self.discipline, status="Закрыта",
            type_of_grade_book="Первичная сдача", number="18.01-23/0011"
        )
        GradebookStudents.objects.create(student=student, gradebook=gradebook, grade="5")
        request = self.client.get(reverse("export_diplom_types") + f"?group={self.group.id}")
        response = export_diplom_types(request)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertTrue("Красный" in content)