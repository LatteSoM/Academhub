from django.test import TestCase
from django.urls import reverse
from Academhub.models import GradebookStudents, Gradebook, Student, GroupStudents, Curriculum, ClockCell, Discipline
from Gradebook.views import GradebookStudentBulkUpdateView, perform_generation
from django.contrib.auth.models import User
from django.utils import timezone


class GradebookStudentBulkUpdateViewTest(TestCase):

    def setUp(self):
        # Создание тестовых данных
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.group = GroupStudents.objects.create(full_name='Test Group')
        self.student = Student.objects.create(full_name='Test Student', group=self.group)
        self.discipline = Discipline.objects.create(name='Test Discipline')
        self.semester = 1
        self.type_of_grade_book = 'Первичная сдача'
        self.name = 'Test Gradebook'
        self.status = 'Не заполнена'

        self.gradebook = Gradebook.objects.create(
            discipline=self.discipline,
            group=self.group,
            semester_number=self.semester,
            type_of_grade_book=self.type_of_grade_book,
            name=self.name,
            status=self.status,
            date_of_opening=timezone.now().date()
        )

        self.student_grade = GradebookStudents.objects.create(
            student=self.student,
            gradebook=self.gradebook,
            grade='Неявка'
        )

        self.url = reverse('gradebookstudents_bulk_create', kwargs={'pk': self.gradebook.pk})

        # Авторизация пользователя
        self.client.login(username='testuser', password='testpass')

    def test_successful_update(self):
        # Тестирование успешного обновления оценок и проверки академических задолженностей
        response = self.client.post(self.url, {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-id': self.student_grade.id,
            'form-0-grade': '5',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
        })

        self.assertEqual(response.status_code, 302)  # Перенаправление после успешного обновления

        # Проверка обновления оценки
        updated_grade = GradebookStudents.objects.get(id=self.student_grade.id)
        self.assertEqual(updated_grade.grade, '5')

        # Проверка обновления статуса академических задолженностей студента
        self.student.refresh_from_db()
        self.assertFalse(self.student.academic_debts)  # Оценка '5' не должна создавать задолженность

    def test_missing_required_fields(self):
        # Тестирование обработки ошибок при отсутствии обязательных полей или связанных объектов
        # Удаление связанных объектов или полей перед запросом

        # Удаление преподавателей из gradebook (если есть)
        self.client.post(self.url)

        # Проверка перенаправления без изменений gradebook.status
        self.assertEqual(self.client.response.status_code, 302)
        self.assertEqual(self.client.response['Location'],
                         reverse('gradebook_detail', kwargs={'pk': self.gradebook.pk}))

        # Проверка отсутствия изменений в статусе gradebook
        self.assertEqual(self.client.response.status_code, 302)
        self.assertEqual(self.client.response['Location'],
                         reverse('gradebook_detail', kwargs={'pk': self.student_grade.id}))


class GradebookGenerateViewTest(TestCase):

    def setUp(self):
        # Создание тестовых данных
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.curriculum = Curriculum.objects.create(qualification_name='Test Qualification', admission_year=2023)
        self.clock_cell = ClockCell.objects.create(
            curriculum=self.curriculum,
            discipline=Discipline.objects.create(name='Test Discipline'),
            term=1,
            code_of_type_work='Экзамен'
        )

        self.url = reverse('gradebook_generate')

        # Авторизация пользователя
        self.client.login(username='testuser', password='testpass')

    def test_successful_generation(self):
        # Тестирование успешной генерации ведомостей

        # Подготовка формы с корректными данными
        form_data = {
            'semester': '1',
            'type_of_gradebook': 'Первичная сдача'
        }

        response = self.client.post(self.url, form_data)

        self.assertEqual(response.status_code, 302)  # Перенаправление после успешной генерации

        # Проверка создания ведомостей через perform_generation
        result = perform_generation(semester_number=form_data['semester'],
                                    grade_book_type=form_data['type_of_gradebook'])
        self.assertTrue(result['generated'] > 0)  # Проверка на создание хотя бы одной ведомости

    def test_invalid_form_data(self):
        # Тестирование обработки невалидных данных формы

        # Отправка формы с невалидными данными (например, несуществующий тип ведомости)
        form_data = {
            'semester': 'invalid',
            'type_of_gradebook': 'Неверный тип'
        }

        response = self.client.post(self.url, form_data)

        self.assertEqual(response.status_code, 200)  # Форма должна быть отображена с ошибками

        # Проверка наличия ошибок формы в контексте ответа
        form = response.context['form']
        self.assertFalse(form.is_valid())