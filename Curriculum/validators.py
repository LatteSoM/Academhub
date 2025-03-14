from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


def validate_snils(value):
    """
    Валидация СНИЛС.
    """
    if not value:
        return

    if not (9 < len(value) < 13):
        raise ValidationError('Длина СНИЛС должна быть 11 или 12 символов.')

    # Дополнительные проверки для СНИЛС (если нужны)

    return value


def validate_full_name(value):
    """
    Валидация ФИО.
    """
    if not value:
        return

    if len(value) < 2:
        raise ValidationError('ФИО должно быть не короче 2 символов.')

    # Дополнительные проверки для ФИО (если нужны)

    return value


def validate_phone(value):
    """
    Валидация номера телефона.
    """
    if not value:
        return

    regex = r'^\+?1?\d{9,15}$'
    if not RegexValidator(regex)(value):
        raise ValidationError('Введите корректный номер телефона.')

    return value