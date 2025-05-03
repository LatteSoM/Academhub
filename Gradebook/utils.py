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

def transliterate(text):
    translit_dict = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh',
        'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O',
        'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts',
        'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu',
        'Я': 'Ya',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
        'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
        'я': 'ya'
    }
    return ''.join(translit_dict.get(char, char) for char in text)