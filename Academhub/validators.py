import re
from django.core.exceptions import ValidationError

def validate_snils(value):
    """Проверяет формат и корректность контрольного числа СНИЛС"""
    pattern = r'^\d{3}-\d{3}-\d{3} \d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Неверный формат СНИЛС. Используйте XXX-XXX-XXX XX')

    # Убираем разделители
    # digits = [int(d) for d in value if d.isdigit()]
    # snils_number = digits[:9]
    # control_sum = digits[-2] * 10 + digits[-1]  # последние 2 цифры - контрольная сумма

    # Вычисляем контрольную сумму по правилам ПФР
    # weighted_sum = sum((i + 1) * num for i, num in enumerate(snils_number))
    #
    # if weighted_sum < 100 and weighted_sum != control_sum:
    #     raise ValidationError('Некорректный СНИЛС: неправильное контрольное число.')
    # elif weighted_sum in (100, 101) and control_sum != 0:
    #     raise ValidationError('Некорректный СНИЛС: неправильное контрольное число.')
    # elif weighted_sum > 101 and (weighted_sum % 101) != control_sum and (weighted_sum % 101) != 0:
    #     raise ValidationError('Некорректный СНИЛС: неправильное контрольное число.')


def validate_full_name(value):
    """Проверяет, что ФИО содержит минимум 2 слова (Фамилия и Имя)"""
    words = value.strip().split()
    if len(words) < 2:
        raise ValidationError('Введите минимум фамилию и имя.')

def validate_phone(value):
    """Проверяет, что телефон состоит только из цифр, +, -, () и начинается с +7 или 8"""
    pattern = r'^(?:\+7|8)\d{10}$'
    digits_only = re.sub(r'\D', '', value)  # Убираем все, кроме цифр

    if not re.match(pattern, value) and not re.match(pattern, digits_only):
        raise ValidationError('Введите корректный номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX')
