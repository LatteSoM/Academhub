import json
import re
from collections import defaultdict

from pyaspeller import YandexSpeller


class MyValidator:
    def __init__(self):
        self.speller = YandexSpeller()
        self.SPELLER_CACHE = {}

    def validate_text(self, text):
        """
        Проверяет текст на наличие ошибок с помощью Yandex Speller,
        игнорируя слова из вайтлиста.
        Возвращает список ошибок или None, если ошибок нет.
        """
        # Если текст уже проверялся – возвращаем результат из кэша
        if text in self.SPELLER_CACHE:
            return self.SPELLER_CACHE[text]

        try:
            changes = self.speller.spell(text)
        except json.JSONDecodeError:
            self.SPELLER_CACHE[text] = []
            return []

        errors = []
        if changes:
            # Пример с использованием словаря whitelist (если понадобится)
            # whitelist_words = get_whitelist()
            for change in changes:
                word_lower = change['word'].lower()
                # if word_lower not in whitelist_words:
                errors.append(
                    f"Возможно ошибка в слове '{change['word']}', "
                    f"возможно имелось в виду: {change['s']}"
                )

        # Если ошибок нет – возвращаем None, иначе список ошибок
        result = errors if errors else None
        self.SPELLER_CACHE[text] = result
        return result


    def validate_discipline_index(self, index: str, previous_indices: dict):
        """
        Проверяет формат индекса дисциплины и последовательность индексов,
        учитывая двусоставные индексы модулей (МДК.01.01).
        """
        if not index:
            return ["Индекс дисциплины отсутствует."]

        index = index.strip()
        index = index.replace("M", "М")  # Заменяем латинскую M на кириллическую М

        if index == "ПОО" or index == "ПДП":
            return None

        match = re.match(r"([\w]+)\.(\d{1,2})(?:\.(\d{1,2}|ЭК))?", index)
        if not match:
            return [f"Неверный формат индекса '{index}'. Ожидается формат 'Префикс.Число' или 'Префикс.Число.Число' или 'Префикс.Число.ЭК'."]

        prefix = match.group(1)
        number_part = match.group(2)
        number_part2 = match.group(3)

        valid_prefixes = {"ОГСЭ", "ЕН", "ОПЦ", "ПЦ", "ПМ", "МДК", "УП", "ПП", "ПДП", "ОП", "ООД", "ГИА", "ПДП", "ПОО"}
        if prefix not in valid_prefixes:
            return [
                f"Недопустимый префикс '{prefix}' в индексе '{index}'. Допустимые префиксы: {', '.join(valid_prefixes)}."]


        # Создаем ключ, включающий номер модуля (МДК.01, МДК.1 и т.д.)
        module_key = f"{prefix}.{number_part}"
        if module_key in previous_indices:
            previus_discipline_index = previous_indices[module_key][-1]
            if previus_discipline_index == number_part2:
                return [f"{index} уже был в учебном плане"]
            elif int(previus_discipline_index)+1 != int(number_part2):
                if int(previus_discipline_index) >= 10:
                    expected_index = str(int(previus_discipline_index))
                else:
                    expected_index = "0" + str(int(previus_discipline_index)+1)
                return [f"Неверная последовательность индекса '{index}'. Ожидается '{prefix}.{number_part}.{expected_index}', так как он должен идти следующим по порядку"]
            else:
                previous_indices[module_key].append(number_part2)
        else:
            previous_indices[module_key].append(number_part2)

        return None

    def validate_discipline_hours(self, discipline):
        """
        Проверяет, что суммарное количество часов за семестр у дисциплины
        равняется сумме часов по всем ячейкам, кроме итоговой.
        """
        total_hours = 0
        all_hours = defaultdict(list)
        itogo_hours = defaultdict(int)
        for cc in discipline.get("clock_cells", []):
            hours = cc.get("count_of_clocks")
            if cc.get("code_of_type_work") == "Итого часов":
                itogo_hours[(cc.get("course"),cc.get("term"))] = hours
            elif hours > 1:
                all_hours[(cc.get("course"),cc.get("term"))].append(hours)


        for course_term, hours in all_hours.items():
            itogo = itogo_hours[course_term]
            total_hours = sum(hours)

            if total_hours != itogo:
                return [
                    f"Обратите внимание на часы дисциплины. Предположительно в ячейке {course_term[0]} курс {course_term[1]} семестр ошибка в часах. Т.к сумма всех ячеек не совпадает с итоговым числом часов"]
        return None
