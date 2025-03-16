import json
import os
from django import forms
from Academhub.models import Specialty, Qualification, Curriculum, Category, StudyCycle, Module, Discipline, Course, Term, ClockCell
from .parser_for_plx import RUP_parser
from datetime import datetime
from pyaspeller import YandexSpeller
import re

class GetPlxForm(forms.Form):
    file = forms.FileField(label="Перетащите файл")
 
    parser = RUP_parser()

    def clean(self):
        super().clean()

        result = self.cleaned_data.get('file')

        if result:
            file_extension = os.path.splitext(result.name)[1]

            if file_extension.lower() != '.plx':
                raise forms.ValidationError("Файл должен быть в формате .plx")
        
            self.get_file_data(result)
            self.load_json_to_models(self.parser.plan_data_json)
    
    def get_file_data(self, file):
        self.parser.add_file(file)
        self.parser.plan_data_json = self.parser.get_plan()
    
    def save(self):
        pass

    def load_json_to_models(self, rup_data):
        """
        Загружает данные из JSON-структуры, сформированной get_plan_rup(),
        в модели Django. Осуществляет предварительное преобразование даты.
        """
        # Очистка базы данных перед загрузкой новых данных
        Curriculum.objects.all().delete()
        Category.objects.all().delete()
        StudyCycle.objects.all().delete()
        Module.objects.all().delete()
        Discipline.objects.all().delete()
        Course.objects.all().delete()
        Term.objects.all().delete()
        ClockCell.objects.all().delete()


        rup_data = json.loads(rup_data)  # Декодируем JSON-строку в словарь

        qualification_name = rup_data.get("qualification")

        # Пытаемся найти квалификацию по имени
        qualification_obj = Qualification.objects.filter(name=qualification_name).first()
        #НУЖНО ДОБАВИТЬ СПЕЦИАЛЬНОСТЬ (пока так, а потом юзер будет выбирать)
        #Добавить возможность юзеру выбирать имеющуюся специальность
        specialnost_mock = Specialty.objects.first()

        # Если не нашли, создаём новую (без привязки к Specialty, т.к. её ID нет в JSON)
        if not qualification_obj:
            qualification_obj = Qualification.objects.get_or_create(
                name=qualification_name,
                short_name=qualification_name[:10],  # Ограничиваем длину короткого названия
                specialty=specialnost_mock
            )
        
        # Создаём объект Curriculum
        curriculum_obj, _ = Curriculum.objects.get_or_create(
        id=rup_data["id"],
        qualification=qualification_obj,
        admission_year=int(rup_data.get("admission_year", 0))  # Преобразуем строку в число
    )

        all_warnings = []  # Список для хранения всех опечаток
        previous_indices = {}  # Словарь для хранения предыдущих индексов

        # Обрабатываем циклы (Category) и дочерние циклы (StudyCycle)
        for cycle in rup_data.get("stady_plan", []):
            # Проверяем имя Category
            category_name = cycle.get("cycles")
            if category_name is not None:
                category_warnings = self.validate_text(category_name)
                if category_warnings:
                    all_warnings.extend(category_warnings)

            category_obj = Category.objects.create(
                id=cycle["id"],
                identificator=cycle.get("identificator"),
                cycles=category_name,
                curriculum=curriculum_obj,
                warnings=bool(category_warnings),
                warning_description=category_warnings
            )
            for child in cycle.get("children", []):
                # Проверяем имя StudyCycle
                study_cycle_name = child.get("cycles")
                if study_cycle_name is not None:
                    study_cycle_warnings = self.validate_text(study_cycle_name)
                    if study_cycle_warnings:
                        all_warnings.extend(study_cycle_warnings)

                study_cycle_obj = StudyCycle.objects.create(
                    id=child["id"],
                    identificator=child.get("identificator"),
                    cycles=study_cycle_name,
                    categories=category_obj,
                    warnings=bool(study_cycle_warnings),
                    warning_description=study_cycle_warnings
                )
                for plan in child.get("plans_of_string", []):
                    # Создаем Module из плана строки
                    module_name = plan.get("discipline")
                    if module_name is not None:
                        module_warnings = self.validate_text(module_name)
                        if module_warnings:
                            all_warnings.extend(module_warnings)
                    module_obj = Module.objects.create(
                        id=plan["id"],
                        discipline=module_name,
                        code_of_discipline=plan.get("code_of_discipline"),
                        code_of_cycle_block=plan.get("code_of_cycle_block"),
                        study_cycles=study_cycle_obj,
                        warnings=bool(module_warnings),
                        warning_description=module_warnings
                    )
                    # Обрабатываем ClockCell для плана (Module)
                    for course in plan.get("clock_cells", []):
                        course_obj = Course.objects.create(
                            id=course['id'],
                            course_number=course['course_number'],
                            module=module_obj
                        )
                        for term in course['terms']:
                            term_obj = Term.objects.create(
                                id=term['id'],
                                term_number=term['term_number'],
                                course=course_obj
                            )
                            for clock in term.get('clock_cells', []):
                                ClockCell.objects.create(
                                    id=clock["id"],
                                    code_of_type_work=clock.get("code_of_type_work"),
                                    code_of_type_hours=clock.get("code_of_type_hours"),
                                    course=clock.get("course"),
                                    term=clock.get("term"),
                                    count_of_clocks=int(clock.get("count_of_clocks") or 0),
                                    term_relation=term_obj
                                )
                    # Обрабатываем дочерние планы строки (Discipline)
                    for child_plan in plan.get("children_strings", []):
                        discipline_name = child_plan.get("discipline")
                        discipline_code = child_plan.get("code_of_discipline")

                        if discipline_name is not None:
                            discipline_warnings = self.validate_text(discipline_name)
                            if discipline_warnings:
                                all_warnings.extend(discipline_warnings)

                        # Валидация индекса
                        index_warnings = self.validate_discipline_index(discipline_code, previous_indices)
                        if index_warnings:
                            print("=== Ошибки валидации индекса ===")
                            for warning in index_warnings:
                                print(warning)

                        discipline_obj = Discipline.objects.create(
                            id=child_plan["id"],
                            name=discipline_name,
                            code=discipline_code,
                            specialty=specialnost_mock,
                            # code_of_cycle_block=child_plan.get("code_of_cycle_block"),
                            module=module_obj,
                            warnings=bool(discipline_warnings or index_warnings),
                            warning_description=discipline_warnings + index_warnings if discipline_warnings and index_warnings else discipline_warnings or index_warnings
                        )
                        curriculum_obj.children_strings.add(discipline_obj)

                        # Вызываем валидацию часов для дисциплины
                        hour_warnings = self.validate_discipline_hours(child_plan)
                        if hour_warnings:
                            all_warnings.extend(hour_warnings)
                            discipline_obj.warnings = True
                            if discipline_obj.warning_description:
                                discipline_obj.warning_description.extend(hour_warnings)
                            else:
                                discipline_obj.warning_description = hour_warnings
                            discipline_obj.save()

                        for course in child_plan.get("clock_cells", []):
                            course_obj = Course.objects.create(
                                id=course['id'],
                                course_number=course['course_number'],
                                disipline=discipline_obj
                            )
                            for term in course['terms']:
                                term_obj = Term.objects.create(
                                    id=term['id'],
                                    term_number=term['term_number'],
                                    course=course_obj
                                )
                                for clock in term.get('clock_cells', []):
                                    ClockCell.objects.create(
                                        id=clock["id"],
                                        code_of_type_work=clock.get("code_of_type_work"),
                                        code_of_type_hours=clock.get("code_of_type_hours"),
                                        course=clock.get("course"),
                                        term=clock.get("term"),
                                        count_of_clocks=int(clock.get("count_of_clocks") or 0),
                                        term_relation=term_obj
                                    )

        print("=== Найденные опечатки ===")
        for warning in all_warnings:
            print(warning)
        
    def validate_text(self, text):
        """
        Проверяет текст на наличие ошибок с помощью Yandex Speller,
        игнорируя слова из вайтлиста.
        Возвращает список ошибок или None, если ошибок нет.
        """
        speller = YandexSpeller()
        changes = speller.spell(text)
        if changes:
            errors = []
            # whitelist_words = get_whitelist()  # Используем кешированное множество
            for change in changes:
                word_lower = change['word'].lower()
                # if word_lower not in whitelist_words:
                #     errors.append(f"Возможно ошибка в слове '{change['word']}' возможно это подходящее слово: {change['s']}")
            return errors
        return None

    def validate_discipline_index(self, index: str, previous_indices: dict):
        """
        Проверяет формат индекса дисциплины и последовательность индексов,
        учитывая двусоставные индексы модулей (МДК.01.01).

        Args:
            index: Индекс дисциплины (например, "МДК.01.01").
            previous_indices: Словарь, хранящий предыдущие индексы.
                            Ключи - комбинация префикса и номера модуля (МДК.01, МДК.1).

        Returns:
            Список ошибок или None, если ошибок нет.
        """
        if not index:
            return ["Индекс дисциплины отсутствует."]

        index = index.strip()

        match = re.match(r"([А-Я]+)\.(\d{1,2}(?:\.\d{1,2})?)", index)
        if not match:
            return [f"Неверный формат индекса '{index}'. Ожидается формат 'Префикс.Число' или 'Префикс.Число.Число'."]

        prefix = match.group(1)
        number_part = match.group(2)

        valid_prefixes = ["ОГСЭ", "ЕН", "ОПЦ", "ПЦ", "ПМ", "МДК", "УП", "ПП", "ПДП"]
        if prefix not in valid_prefixes:
            return [f"Недопустимый префикс '{prefix}' в индексе '{index}'. Допустимые префиксы: {', '.join(valid_prefixes)}."]

        if "." in number_part:
            main_number_str, secondary_number_str = number_part.split(".")
            main_number, secondary_number = int(main_number_str), int(secondary_number_str)
        else:
            main_number_str = number_part
            main_number = int(main_number_str)
            secondary_number = None

        # Создаем ключ, включающий номер модуля (МДК.01, МДК.1 и т.д.)
        module_key = f"{prefix}.{main_number_str}"

        if module_key not in previous_indices:
            previous_indices[module_key] = (None, None)  # Инициализируем запись

        prev_main, prev_secondary = previous_indices[module_key]

        if prev_main is None:  # Первый индекс для данного модуля
            if secondary_number is None and main_number != int(main_number_str): #проверка на валидность индекса, если он без подчасти
                return [f"Неверная последовательность индекса '{index}'. Ожидается '{prefix}.1' или '{prefix}.01'."]
            if secondary_number is not None and secondary_number != 1:
                return [f"Неверная последовательность индекса '{index}'. Ожидается '{prefix}.{main_number_str}.1' или '{prefix}.0{main_number_str}.01'."]
            previous_indices[module_key] = (main_number, secondary_number)
        else:  # Индекс для данного модуля уже существует
            if secondary_number is None:  # Если текущий индекс - "Префикс.Число"
                if prev_secondary is not None:
                    return [f"Неверная последовательность индекса '{index}'. Индекс с одной цифрой не может идти после индекса с двумя."]
                if main_number != prev_main + 1:
                    return [f"Неверная последовательность индекса '{index}'. Ожидается '{prefix}.{prev_main + 1}'."]
                previous_indices[module_key] = (main_number, None)
            else:  # Если текущий индекс - "Префикс.Число.Число"
                if prev_secondary is None:
                    if main_number != prev_main or secondary_number != 1:
                        return [f"Неверная последовательность индекса '{index}'. Ожидается '{prefix}.{prev_main}.1'."]
                else:
                    if main_number != prev_main or secondary_number != prev_secondary + 1:
                        return [f"Неверная последовательность индекса '{index}'. Ожидается '{prefix}.{prev_main}.{prev_secondary + 1}'."]
                previous_indices[module_key] = (main_number, secondary_number)

        return None

    def validate_discipline_hours(self, discipline):
        """
        Проверяет, что суммарное количество часов за семестр у дисциплины
        равняется сумме часов по всем ячейкам, кроме итоговой.
        """
        for course in discipline.get("clock_cells", []):
            for term in course.get('terms', []):
                total_hours = 0
                max_hours = 0
                for clock in term.get('clock_cells', []):
                    count_of_clocks = clock.get("count_of_clocks", 0)
                    total_hours += count_of_clocks
                    if count_of_clocks > max_hours:
                        max_hours = count_of_clocks

                if total_hours - max_hours != max_hours:
                    return [f"Сумма часов по ячейкам ({total_hours - max_hours}) не совпадает с итоговым количеством часов ({max_hours}) за семестр {term['term_number']} курса {course['course_number']} у дисциплины '{discipline.get('discipline')}'."]
        return None
    
        