import logging

from Academhub.models import Gradebook
logger = logging.getLogger(__name__)


def update_gradebooks_after_deactivation(teachers):
    """
    Удаляет деактивированных преподавателей из ведомостей и обновляет статус.

    Args:
        teachers (QuerySet): Список деактивированных преподавателей.
    """
    try:
        # Получаем ведомости со статусом "Открыта" или "Не заполнена"
        gradebooks = Gradebook.objects.filter(status__in=['Открыта', 'Не заполнена'])

        if not gradebooks.exists():
            logger.info("Нет ведомостей со статусом 'Открыта' или 'Не заполнена' для обработки.")
            return

        # Обрабатываем каждую ведомость
        for gradebook in gradebooks:
            # Проверяем, есть ли деактивированные преподаватели в ведомости
            teachers_to_remove = gradebook.teachers.filter(id__in=teachers.values_list('id', flat=True))

            if teachers_to_remove.exists():
                # Удаляем преподавателей из ведомости
                gradebook.teachers.remove(*teachers_to_remove)

                # Устанавливаем статус "Не заполнена"
                gradebook.status = 'Не заполнена'
                gradebook.save()

                logger.info(
                    f"Ведомость {gradebook.number} ({gradebook.name}) обновлена: удалены преподаватели {list(teachers_to_remove.values_list('email', flat=True))}, статус изменен на 'Не заполнена'.")
            else:
                logger.debug(
                    f"Ведомость {gradebook.number} ({gradebook.name}) не содержит деактивированных преподавателей.")

    except Exception as e:
        logger.error(f"Ошибка при обновлении ведомостей: {str(e)}")
        raise