from celery import shared_task
from Academhub.models import Gradebook, GradebookStudents
from Gradebook.utils import perform_generation

@shared_task
def generate_gradebooks_task(semester_number, grade_book_type, request_user_id):
    result = perform_generation(semester_number, grade_book_type)
    success_part = []
    if result['generated'] > 0:
        success_part.append(f"сгенерировано {result['generated']}")
    if result['updated'] > 0:
        success_part.append(f"обновлено {result['updated']}")
    if success_part:
        success_message = " и ".join(success_part)
        message = f"Успешно {success_message} ведомостей для {semester_number} семестра! С типом {result['grade_book_type']}. Ошибок: {result['errors']}"
    else:
        message = "Не удалось сгенерировать ни одной ведомости!"
    return message