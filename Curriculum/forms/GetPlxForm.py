import os
import json
from django import forms
from collections import defaultdict
from ..utils.utils import MyValidator
from ..parser_for_plx import RUP_parser
from ..models.models_dict_sesstion import *
from Academhub.models import Specialty, Qualification


class GetPlxForm(forms.Form):
    """
    Форма для загрузки PLX-файла, выбора специальности и парсинга данных.
    """
    file = forms.FileField(label="Перетащите файл")
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(), required=True, label="Специальность"
    )

    basises = [
        (9, '9 класс'),
        (11, '11 класс'),
    ]

    basis_of_admission = forms.ChoiceField(choices=basises, label='Выберите основу обучения')

    parser = RUP_parser()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.validator = MyValidator()
        super().__init__(*args, **kwargs)


    def clean(self):
        """
        Валидирует данные формы, проверяет расширение файла, парсит данные из файла
        и сохраняет их в сессию.
        """
        super().clean()
        result = self.cleaned_data.get('file')
        specialty = self.cleaned_data.get('specialty')
        basis_of_admission = self.cleaned_data.get('basis_of_admission')

        if result:
            file_extension = os.path.splitext(result.name)[1]
            if file_extension.lower() != '.plx':
                raise forms.ValidationError("Файл должен быть в формате .plx")

            self.get_file_data(result)
            created_objects = self.load_json_to_models(self.parser.plan_data_json, specialty, basis_of_admission)
            self.request.session['uploaded_data'] = json.dumps(created_objects, default=str) # Сериализуем и сохраняем в сессию

    def get_file_data(self, file):
        """
        Получает данные из загруженного файла, используя парсер.
        """
        self.parser.add_file(file)
        self.parser.plan_data_json = self.parser.get_plan()
    #Мы не сохраняем данные т.к их нужно проверить сперва человеку в формочке Edit
    def save(self):
        """
        Этот метод не сохраняет данные, так как они должны быть проверены
        пользователем в форме редактирования.
        """
        pass

    def load_json_to_models(self, rup_data, specialty, basis_of_admission):
        """
        Загружает данные из JSON-структуры, полученной из PLX-файла,
        в структуры данных Python (словари и списки).
        Производит преобразование данных и возвращает словарь с созданными объектами,
        готовыми для отображения в форме редактирования.
        """
        # Приведём специальность к словарю для дальнейшей передачи через json
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
            admission_year=int(rup_data.get("admission_year", 0)), # Преобразуем строку в число
            basis_of_admission=int(basis_of_admission)
        )
        curriculum_obj = curriculum_obj.to_dict()

        all_warnings = []  # Список для хранения всех опечаток
        previous_indices = defaultdict(list)  # Словарь для хранения предыдущих индексов

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
                category_warnings = None #Если хотим проверять - используем validate_text
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
                    study_cycle_warnings = None #Если хотим проверять - используем validate_text
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
                    if module_name == "Дисциплины по выбору (предлагаемые ОО)":
                        pass
                    if module_name is not None:
                        module_warnings = None #Если хотим проверять - используем validate_text
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

                        if discipline_name == "Дисциплины по выбору (предлагаемые ОО)":
                            pass

                        if discipline_name is not None:
                            discipline_warnings = self.validator.validate_text(text=discipline_name)
                            if discipline_warnings:
                                all_warnings.extend(discipline_warnings)

                        # Валидация индекса
                        index_warnings = self.validator.validate_discipline_index(discipline_code, previous_indices)
                        # Вызываем валидацию часов для дисциплины
                        all_bad_hour, all_warning_description = self.validator.validate_discipline_hours(discipline)

                        discipline_obj = DisciplineDict(
                            discipline_name=discipline_name,
                            code=discipline_code,
                            specialty=specialty,
                            module=module_obj,
                            cycle_relation=discipline.get("cycle_relation"),
                            warnings=bool(discipline_warnings or index_warnings or len(all_bad_hour) > 0),
                            warning_description=discipline_warnings + index_warnings + all_warning_description if discipline_warnings and index_warnings else discipline_warnings or index_warnings
                        )

                        if len(all_bad_hour) > 0:
                            discipline_obj.warning = True
                            if discipline_obj.warning_description:
                                discipline_obj.warning_description.extend(all_warning_description)
                            else:
                                discipline_obj.warning_description = all_warning_description

                        created_objects["disciplines"].append(discipline_obj.to_dict())

                        for clock in discipline.get("clock_cells", []):
                            course = clock.get("course")
                            term = clock.get("term")

                            if course == 2:
                                if term == 1:
                                    term = 3
                                elif term == 2:
                                    term = 4
                            elif course == 3:
                                if term == 1:
                                    term = 5
                                elif term == 2:
                                    term = 6
                            elif course == 4:
                                if term == 1:
                                    term = 7
                                elif term == 2:
                                    term = 8

                            clock_cell_obj = ClockCellDict(
                                code_of_type_work=clock.get("code_of_type_work"),
                                code_of_type_hours=clock.get("code_of_type_hours"),
                                course=course,
                                term=term,
                                count_of_clocks=int(clock.get("count_of_clocks") or 0),
                                module=None,
                                discipline=f"{discipline_obj.code}.{discipline_obj.discipline_name}",
                                curriculum=curriculum_obj,
                                warnings=True if (course, term) in all_bad_hour else False,
                                warning_description="Описание в описании дисциплины",
                            ).to_dict()
                            created_objects["clock_cells"].append(clock_cell_obj)  # Добавляем в словарь

            for discipline_cycle in cycle.get("children", []):
                for discipline in discipline_cycle.get("disciplines", []):
                    discipline_name = discipline.get("discipline_name")
                    discipline_code = discipline.get("code_of_discipline")

                    if discipline_name is not None:
                        discipline_warnings = self.validator.validate_text(discipline_name)
                        if discipline_warnings:
                            all_warnings.extend(discipline_warnings)

                    # Валидация индекса
                    index_warnings = self.validator.validate_discipline_index(discipline_code, previous_indices)

                    # Вызываем валидацию часов для дисциплины
                    all_bad_hour, all_warning_description = self.validator.validate_discipline_hours(discipline)

                    discipline_obj = DisciplineDict(
                        discipline_name=discipline_name,
                        code=discipline_code,
                        specialty=specialty,
                        module=module_obj,
                        cycle_relation=discipline.get("cycle_relation"),
                        warnings=bool(discipline_warnings or index_warnings or len(all_bad_hour) > 0),
                        warning_description=discipline_warnings + index_warnings + all_warning_description if discipline_warnings and index_warnings else discipline_warnings or index_warnings
                    )

                    if len(all_bad_hour) > 0:
                        discipline_obj.warning = True
                        if discipline_obj.warning_description:
                            discipline_obj.warning_description.extend(all_warning_description)
                        else:
                            discipline_obj.warning_description = all_warning_description

                    created_objects["disciplines"].append(discipline_obj.to_dict())

                    for clock in discipline.get("clock_cells", []):
                        course = clock.get("course")
                        term = clock.get("term")

                        if course == 2:
                            if term == 1:
                                term = 3
                            elif term == 2:
                                term = 4
                        elif course == 3:
                            if term == 1:
                                term = 5
                            elif term == 2:
                                term = 6
                        elif course == 4:
                            if term == 1:
                                term = 7
                            elif term == 2:
                                term = 8

                        clock_cell_obj = ClockCellDict(
                            code_of_type_work=clock.get("code_of_type_work"),
                            code_of_type_hours=clock.get("code_of_type_hours"),
                            course=course,
                            term=term,
                            count_of_clocks=int(clock.get("count_of_clocks") or 0),
                            module=None,
                            discipline=f"{discipline_obj.code}.{discipline_obj.discipline_name}",
                            curriculum=curriculum_obj,
                            warnings=True if (course, term) in all_bad_hour else False,
                            warning_description="Описание в описании дисциплины",
                        ).to_dict()
                        created_objects["clock_cells"].append(clock_cell_obj)  # Добавляем в словарь

        return created_objects # Возвращаем словарь с созданными объектами