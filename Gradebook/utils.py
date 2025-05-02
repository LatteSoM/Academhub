import logging

from Academhub.models import Gradebook
logger = logging.getLogger(__name__)

def update_statements_after_deactivation(teachers):
    """
    Удаляет деактивированных преподавателей из ведомостей и обновляет статус.

    Args:
        teachers (QuerySet): Список деактивированных преподавателей.
    """
    try:
        # Получаем ведомости со статусом OPEN или NOT_FILLED
        statements = Gradebook.objects.filter(status__in=['Открыта', 'Не заполнена'])

        if not statements.exists():
            logger.info("Нет ведомостей со статусом Открыта или Не заполнена для обработки.")
            return

        # Обрабатываем каждую ведомость
        for statement in statements:
            # Проверяем, есть ли деактивированные преподаватели в ведомости
            teachers_to_remove = statement.teachers.filter(id__in=teachers.values_list('id', flat=True))

            if teachers_to_remove.exists():
                # Удаляем преподавателей из ведомости
                statement.teachers.remove(*teachers_to_remove)

                # Обновляем статус на NOT_FILLED
                statement.status = 'NOT_FILLED'
                statement.save()

                logger.info(
                    f"Ведомость {statement.title} обновлена: удалены преподаватели {list(teachers_to_remove.values_list('email', flat=True))}, статус изменен на NOT_FILLED.")
            else:
                logger.debug(f"Ведомость {statement.title} не содержит деактивированных преподавателей.")

    except Exception as e:
        logger.error(f"Ошибка при обновлении ведомостей: {str(e)}")
        raise