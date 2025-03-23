import json
import os
import re
from collections import defaultdict

from django import forms
from pyaspeller import YandexSpeller

from Academhub.models import Specialty, Qualification, Category, Curriculum, StudyCycle, Module, Discipline, \
    ClockCell
from .models.models_dict_sesstion import *
from .parser_for_plx import RUP_parser


class GetPlxForm(forms.Form):
    file = forms.FileField(label="Перетащите файл")
    specialty = forms.ModelChoiceField(queryset=Specialty.objects.all(), required=True, label="Специальность")
    parser = RUP_parser()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        result = self.cleaned_data.get('file')
        specialty = self.cleaned_data.get('specialty')

        if result:
            file_extension = os.path.splitext(result.name)[1]
            if file_extension.lower() != '.plx':
                raise forms.ValidationError("Файл должен быть в формате .plx")

            self.get_file_data(result)
            created_objects = self.load_json_to_models(self.parser.plan_data_json, specialty)
            self.request.session['uploaded_data'] = json.dumps(created_objects, default=str) # Сериализуем и сохраняем в сессию

    def get_file_data(self, file):
        self.parser.add_file(file)
        self.parser.plan_data_json = self.parser.get_plan()
    #Мы не сохраняем данные т.к их нужно проверить сперва человеку в формочке Edit
    def save(self):
        pass

    def load_json_to_models(self, rup_data, specialty):
        """
        Загружает данные из JSON-структуры, сформированной get_plan_rup(),
        в модели Django. Осуществляет предварительное преобразование даты и валидацию,
        но не сохраняет в базу данных. Возвращает словарь с созданными объектами.
        """
        #Приведём специальность к словарю для дальнейшей передачи через json
        specialty = SpecialtyDict(code=specialty.code, name=specialty.name).to_dict()
        qualification_name = rup_data.get("qualification")


        # Пытаемся найти квалификацию по имени
        tmp = Qualification.objects.filter(name=qualification_name).first()
        # Если не нашли, создаём новую
        if not tmp:
            qualification_obj = QualificationDict(
                name=qualification_name,
                short_name=qualification_name[:10], # Заглушка
                specialty=specialty,
            )
        else:
            qualification_obj = QualificationDict(
                short_name = tmp.short_name,
                name = tmp.name,
                specialty = specialty,
            )
        qualification_obj = qualification_obj

        # Создаём объект Curriculum
        curriculum_obj = CurriculumDict(
            qualification_name=qualification_obj.name,
            qualification=qualification_obj.to_dict(),
            admission_year=int(rup_data.get("admission_year", 0))  # Преобразуем строку в число
        )
        curriculum_obj = curriculum_obj.to_dict()

        all_warnings = []  # Список для хранения всех опечаток
        previous_indices = {}  # Словарь для хранения предыдущих индексов

        created_objects = {  # Словарь для хранения созданных объектов и дальнейшей передачи в сессию
            "curriculum": [curriculum_obj],
            "categories": [],
            "study_cycles": [],
            "modules": [],
            "disciplines": [],
            "courses": [],
            "terms": [],
            "clock_cells": []
        }

        # Обрабатываем циклы (Category) и дочерние циклы (StudyCycle)
        for cycle in rup_data.get("stady_plan", []):
            # Проверяем имя Category
            category_name = cycle.get("cycles")
            if category_name is not None:
                category_warnings = self.validate_text(category_name)
                if category_warnings:
                    all_warnings.extend(category_warnings)

            category_obj = CategoryDict(
                identificator=cycle.get("identificator"),
                cycles=category_name,
                curriculum=curriculum_obj,
                warnings=bool(category_warnings),
                warning_description=category_warnings
            ).to_dict()
            created_objects["categories"].append(category_obj) # Добавляем в словарь

            for child in cycle.get("children", []):
                # Проверяем имя StudyCycle
                study_cycle_name = child.get("cycles")
                if study_cycle_name is not None:
                    study_cycle_warnings = self.validate_text(study_cycle_name)
                    if study_cycle_warnings:
                        all_warnings.extend(study_cycle_warnings)

                study_cycle_obj = StudyCycleDict(
                    identificator=child.get("identificator"),
                    cycles=study_cycle_name,
                    categories=category_obj,
                    warnings=bool(study_cycle_warnings),
                    warning_description=study_cycle_warnings
                ).to_dict()
                created_objects["study_cycles"].append(study_cycle_obj) # Добавляем в словарь

                for plan in child.get("modules", []):
                    # Создаем Module из модуля
                    module_name = plan.get("module_name")
                    if module_name is not None:
                        module_warnings = self.validate_text(module_name)
                        if module_warnings:
                            all_warnings.extend(module_warnings)
                    module_obj = ModuleDict(
                        module_name=module_name,
                        code_of_discipline=plan.get("code_of_discipline"),
                        code_of_cycle_block=plan.get("code_of_cycle_block"),
                        study_cycles=study_cycle_obj,
                        warnings=bool(module_warnings),
                        warning_description=module_warnings
                    ).to_dict()
                    created_objects["modules"].append(module_obj) # Добавляем в словарь

                    for clock in plan.get("clock_cells", []):
                        clock_cell_obj = ClockCellDict(
                            code_of_type_work=clock.get("code_of_type_work"),
                            code_of_type_hours=clock.get("code_of_type_hours"),
                            course=clock.get("course"),
                            term=clock.get("term"),
                            count_of_clocks=int(clock.get("count_of_clocks") or 0),
                            module=module_obj,
                            discipline=None,
                            curriculum=curriculum_obj,
                        ).to_dict()
                        created_objects["clock_cells"].append(clock_cell_obj)  # Добавляем в словарь

                    # Обрабатываем дочерние планы строки (Discipline)
                    for discipline in plan.get("disciplines", []):
                        discipline_name = discipline.get("discipline_name")
                        discipline_code = discipline.get("code_of_discipline")

                        if discipline_name is not None:
                            discipline_warnings = self.validate_text(discipline_name)
                            if discipline_warnings:
                                all_warnings.extend(discipline_warnings)

                        # Валидация индекса
                        index_warnings = self.validate_discipline_index(discipline_code, previous_indices)
                        if index_warnings:
                            # print("=== Ошибки валидации индекса ===")
                            for warning in index_warnings:
                                pass
                                # print(warning)

                        discipline_obj = DisciplineDict(
                            discipline_name=discipline_name,
                            code=discipline_code,
                            specialty=specialty,
                            module=module_obj,
                            cycle_relation=discipline.get("cycle_relation"),
                            warnings=bool(discipline_warnings or index_warnings),
                            warning_description=discipline_warnings + index_warnings if discipline_warnings and index_warnings else discipline_warnings or index_warnings
                        )

                        # Вызываем валидацию часов для дисциплины
                        hour_warnings = self.validate_discipline_hours(discipline)
                        if hour_warnings:
                            all_warnings.extend(hour_warnings)
                            discipline_obj.warning = True
                            if discipline_obj.warning_description:
                                discipline_obj.warning_description.extend(hour_warnings)
                            else:
                                discipline_obj.warning_description = hour_warnings

                        created_objects["disciplines"].append(discipline_obj.to_dict())

                        for clock in discipline.get("clock_cells", []):
                            clock_cell_obj = ClockCellDict(
                                code_of_type_work=clock.get("code_of_type_work"),
                                code_of_type_hours=clock.get("code_of_type_hours"),
                                course=clock.get("course"),
                                term=clock.get("course")*clock.get("term"),
                                count_of_clocks=int(clock.get("count_of_clocks") or 0),
                                module=None,
                                discipline=discipline_obj.discipline_name,
                                curriculum=curriculum_obj,
                            ).to_dict()
                            created_objects["clock_cells"].append(clock_cell_obj)  # Добавляем в словарь

                for discipline_cycle in cycle.get("children", []):
                    for discipline in discipline_cycle.get("disciplines", []):
                        discipline_name = discipline.get("discipline_name")
                        discipline_code = discipline.get("code_of_discipline")

                        if discipline_name is not None:
                            discipline_warnings = self.validate_text(discipline_name)
                            if discipline_warnings:
                                all_warnings.extend(discipline_warnings)

                        # Валидация индекса
                        index_warnings = self.validate_discipline_index(discipline_code, previous_indices)
                        if index_warnings:
                            # print("=== Ошибки валидации индекса ===")
                            for warning in index_warnings:
                                pass
                                # print(warning)

                        discipline_obj = DisciplineDict(
                            discipline_name=discipline_name,
                            code=discipline_code,
                            specialty=specialty,
                            cycle_relation=discipline.get("cycle_relation"),
                            warnings=bool(discipline_warnings or index_warnings),
                            warning_description=discipline_warnings + index_warnings if discipline_warnings and index_warnings else discipline_warnings or index_warnings
                        )

                        # Вызываем валидацию часов для дисциплины
                        hour_warnings = self.validate_discipline_hours(discipline)
                        if hour_warnings:
                            all_warnings.extend(hour_warnings)
                            discipline_obj.warning = True
                            if discipline_obj.warning_description:
                                discipline_obj.warning_description.extend(hour_warnings)
                            else:
                                discipline_obj.warning_description = hour_warnings

                        created_objects["disciplines"].append(discipline_obj.to_dict())

                        for clock in discipline.get("clock_cells", []):
                            clock_cell_obj = ClockCellDict(
                                code_of_type_work=clock.get("code_of_type_work"),
                                code_of_type_hours=clock.get("code_of_type_hours"),
                                course=clock.get("course"),
                                term=clock.get("course")*clock.get("term"),
                                count_of_clocks=int(clock.get("count_of_clocks") or 0),
                                module=None,
                                discipline=discipline_obj.discipline_name,
                                curriculum=curriculum_obj,
                            ).to_dict()
                            created_objects["clock_cells"].append(clock_cell_obj)  # Добавляем в словарь

        return created_objects # Возвращаем словарь с созданными объектами

    def validate_text(self, text):
        """
        Проверяет текст на наличие ошибок с помощью Yandex Speller,
        игнорируя слова из вайтлиста.
        Возвращает список ошибок или None, если ошибок нет.
        """
        speller = YandexSpeller()
        try:
            changes = speller.spell(text)
        except json.JSONDecodeError:
            # Либо можно залогировать ошибку, либо вернуть пустой список
            return []
        if changes:
            errors = []
            # whitelist_words = get_whitelist()
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

        valid_prefixes = ["ОГСЭ", "ЕН", "ОПЦ", "ПЦ", "ПМ", "МДК", "УП", "ПП", "ПДП", "ОП"]
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

class EditableCurriculumForm(forms.Form):
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_objects = json.loads(data) if isinstance(data, str) else data
        self.generate_fields_for_edit_descipline()

    def generate_fields_for_edit_descipline(self):
        disciplines_data = self.data_objects.get('disciplines', [])
        clock_cells = self.data_objects.get('clock_cells', [])

        # Структура: { discipline_name: { term: суммарное_значение_count_of_clocks } }
        clock_cell_lookup = defaultdict(lambda: defaultdict(int))
        for cell in clock_cells:
            discipline_name = cell.get('discipline')
            if not discipline_name:
                continue
            term = cell.get('term')
            count = cell.get('count_of_clocks', 0)
            if cell.get("code_of_type_work") == 'Итого часов' and clock_cell_lookup[discipline_name][term] == 0:
                clock_cell_lookup[discipline_name][term] += count
            if discipline_name == "Основы философии":
                pass

        # Генерация полей формы для каждой дисциплины
        for i, discipline_data in enumerate(disciplines_data):
            # Скрытое поле для ID дисциплины
            self.fields[f'discipline_id_{i}'] = forms.CharField(
                initial=discipline_data.get('id'),
                widget=forms.HiddenInput()
            )

            # Поле для названия дисциплины
            self.fields[f'discipline_name_{i}'] = forms.CharField(
                initial=discipline_data.get('name', ''),
                label=f'Дисциплина №{i}',
                required=True
            )

            # Поле для кода дисциплины
            self.fields[f'discipline_code_{i}'] = forms.CharField(
                initial=discipline_data.get('code', ''),
                label=f'Код дисциплины №{i}',
                required=True
            )

            # Установка атрибутов предупреждений, если они есть
            if discipline_data.get('warnings', False):
                self.fields[f'discipline_name_{i}'].warnings = True
                self.fields[f'discipline_name_{i}'].warning_description = discipline_data.get('warning_description', [])
                self.fields[f'discipline_code_{i}'].warnings = True
                self.fields[f'discipline_code_{i}'].warning_description = discipline_data.get('warning_description', [])


            disc_name = discipline_data.get('name')

            # Генерация дополнительных полей для 8 семестров
            for semester in range(1, 9):
                field_name = f'discipline_semester_{semester}_{i}'

                # Получаем часы из clock_cell_lookup, если они есть
                initial_value = clock_cell_lookup.get(disc_name, {}).get(semester, 0)

                self.fields[field_name] = forms.IntegerField(
                    initial=initial_value,
                    label=f'Семестр {semester}',
                    required=False
                )
                # Если у дисциплины есть предупреждения, устанавливаем их и для поля с часами
                if discipline_data.get('warnings', False):
                    self.fields[field_name].warnings = True
                    self.fields[field_name].warning_description = discipline_data.get('warning_description', [])

    def get_disciplines_data_from_edit_field(self):
        disciplines_data = []
        for field_name, field in self.fields.items():
            if field_name.startswith('discipline_id_'):
                index = field_name[len('discipline_id_'):]
                discipline = {
                    'id': self.data.get(f'discipline_id_{index}'),
                    'name': self.data.get(f'discipline_name_{index}'),
                    'code': self.data.get(f'discipline_code_{index}'),
                    # Собираем данные по семестрам в отдельный словарь
                    'clock_cell': {
                        f'semester_{s}': self.data.get(f'discipline_semester_{s}_{index}')
                        for s in range(1, 9)
                    }
                }
                disciplines_data.append(discipline)
        return disciplines_data

    def save(self):
        disciplines_data = self.get_disciplines_data_from_edit_field()
        data_objects = self.data_objects

        # Restore Curriculum
        restored_curriculum = Curriculum.from_dict(data_objects.get("curriculum")[0])
        restored_curriculum.save()

        # Restore Categories
        restored_categories = []
        for cat_data in data_objects.get("categories", []):
            category_obj = Category(
                identificator=cat_data["identificator"],
                cycles=cat_data["cycles"],
                curriculum=restored_curriculum,
                warnings=cat_data["warnings"],
                warning_description=cat_data["warning_description"]
            )
            category_obj.save()
            restored_categories.append(category_obj)

        # Restore Study Cycles
        restored_study_cycles = []
        for sc_data in data_objects.get("study_cycles", []):

            study_cycle_obj = StudyCycle(
                identificator=sc_data["identificator"],
                cycles=sc_data["cycles"],
                categories=next((cat for cat in restored_categories if cat.identificator == sc_data["categories"]["identificator"]), None),
                warnings=sc_data["warnings"],
                warning_description=sc_data["warning_description"]
            )
            study_cycle_obj.save()
            restored_study_cycles.append(study_cycle_obj)

        # Restore Modules
        restored_modules = []
        for m_data in data_objects.get("modules", []):
            module_obj = Module(
                name=m_data["module_name"],
                code_of_discipline=m_data["code_of_discipline"],
                code_of_cycle_block=m_data["code_of_cycle_block"],
                study_cycles=next((sc for sc in restored_study_cycles if sc.identificator == m_data["study_cycles"]["identificator"]), None),
                warnings=m_data["warnings"],
                warning_description=m_data["warning_description"]
            )
            module_obj.save()
            restored_modules.append(module_obj)

        # Restore Disciplines
        restored_disciplines = []
        for discipline_id, d_data in enumerate(data_objects.get("disciplines", [])):
            discipline_data = disciplines_data[discipline_id]

            prompt = Discipline.objects.filter(name=discipline_data['name'])
            discipline = prompt[0] if prompt else None

            if discipline:
                discipline.modules.set([m for m in restored_modules if m.name == (d_data["module"]["module_name"] if d_data["module"] else None)])
                discipline.study_cycles.set([rsc for rsc in restored_study_cycles if rsc.cycles == d_data["cycle_relation"]])

                discipline.save()

                restored_disciplines.append(discipline)

            else:
                discipline_obj = Discipline(
                    code=discipline_data["code"],
                    name=discipline_data["name"],
                    specialty=Specialty.from_dict(d_data["specialty"]),
                    warnings=d_data["warnings"],
                    warning_description=d_data["warning_description"]
                )

                discipline_obj.save()

                discipline_obj.modules.set([m for m in restored_modules if m.name == (d_data["module"]["module_name"] if d_data["module"] else None)])
                discipline_obj.study_cycles.set([rsc for rsc in restored_study_cycles if rsc.cycles == d_data["cycle_relation"]])

                discipline_obj.save()

                restored_disciplines.append(discipline_obj)

        # Restore Clock Cells
        restored_clock_cells = []
        for cc_data in data_objects.get("clock_cells", []):
            # Проверка на то, что ячейка имеет связь с модулем либо дисциплиной. Если и того и того нет - скипаем
            module = next((m for m in restored_modules if m.name == (cc_data["module"]["module_name"] if cc_data["module"] else None)), None)
            discipline = next((d for d in restored_disciplines if d.name == (cc_data["discipline"] if cc_data["discipline"] else None)), None)

            clock_cell_obj = ClockCell(
                code_of_type_work=cc_data["code_of_type_work"],
                code_of_type_hours=cc_data["code_of_type_hours"],
                course=cc_data["course"],
                term=cc_data["term"],
                count_of_clocks=cc_data["count_of_clocks"],
                module=module,
                discipline=discipline,
                curriculum=restored_curriculum,
            )
            clock_cell_obj.save()
            restored_clock_cells.append(clock_cell_obj)

