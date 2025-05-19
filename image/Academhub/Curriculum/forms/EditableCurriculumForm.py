import json
from collections import defaultdict

from django import forms

from Academhub.models import Specialty, Category, Curriculum, StudyCycle, Module, Discipline, ClockCell


class EditableCurriculumForm(forms.Form):
    def __init__(self, json_data, data=None, *args, **kwargs):
        self.data_objects = json.loads(json_data) if isinstance(json_data, str) else json_data
        super().__init__(data, *args, **kwargs)
        self.generate_fields_for_edit_descipline()

    def generate_fields_for_edit_descipline(self):
        # 1. Поля для Curriculum (год поступления, квалификация)
        curriculum_list = self.data_objects.get("curriculum", [])
        if curriculum_list:
            curriculum_data = curriculum_list[0]
            self.fields["admission_year"] = forms.IntegerField(
                initial=curriculum_data.get("admission_year", 0),
                label="Год поступления",
                required=False
            )
            qualification_data = curriculum_data.get("qualification", {})
            self.fields["qualification_name"] = forms.CharField(
                initial=qualification_data.get("name", ""),
                label="Квалификация",
                required=False
            )

        # 2. Поля для дисциплин
        disciplines_data = self.data_objects.get('disciplines', [])
        clock_cells = self.data_objects.get('clock_cells', [])
        clock_cell_lookup = defaultdict(lambda: defaultdict(int))
        for cell in clock_cells:
            discipline_name = cell.get('discipline')
            if not discipline_name:
                continue
            term = cell.get('term')
            count = cell.get('count_of_clocks', 0)
            if cell.get("code_of_type_work") == 'Итого часов' and clock_cell_lookup[discipline_name][term] == 0:
                clock_cell_lookup[discipline_name][term] += count

        # Генерация полей для каждой дисциплины
        for i, discipline_data in enumerate(disciplines_data):
            self.fields[f'discipline_id_{i}'] = forms.CharField(
                initial=discipline_data.get('id'),
                widget=forms.HiddenInput()
            )
            self.fields[f'discipline_name_{i}'] = forms.CharField(
                initial=discipline_data.get('name', ''),
                label=f'Дисциплина №{i}',
                required=True
            )
            self.fields[f'discipline_code_{i}'] = forms.CharField(
                initial=discipline_data.get('code', ''),
                label=f'Код дисциплины №{i}',
                required=True
            )
            # Если для дисциплины задано предупреждение, задаём его для полей имени и кода
            if discipline_data.get('warnings', False):
                self.fields[f'discipline_name_{i}'].warnings = True
                self.fields[f'discipline_name_{i}'].warning_description = discipline_data.get('warning_description', [])
                self.fields[f'discipline_code_{i}'].warnings = True
                self.fields[f'discipline_code_{i}'].warning_description = discipline_data.get('warning_description', [])
            disc_name = discipline_data.get('name')
            disc_code = discipline_data.get('code')
            # Для каждого семестра
            # В методе generate_fields_for_edit_descipline после создания полей семестров
            for semester in range(1, 9):
                field_name = f'discipline_semester_{semester}_{i}'
                initial_value = clock_cell_lookup.get(f"{disc_code}.{disc_name}", {}).get(semester, 0)
                self.fields[field_name] = forms.IntegerField(
                    initial=initial_value,
                    label=f'Семестр {semester}',
                    required=False
                )

                if discipline_data.get('warnings', False):
                    self.fields[field_name].warnings = True
                    # Добавляем специфичное описание для часов, если оно есть
                    hours_warning = next((warn for warn in discipline_data.get('warning_description', [])
                                          if f'семестр {semester}' in warn.lower()), None)
                    if hours_warning:
                        self.fields[field_name].warning_description = [hours_warning]
                    else:
                        self.fields[field_name].warning_description = discipline_data.get('warning_description', [])

    def get_disciplines_data_from_edit_field(self):
        # Если пришли динамические данные – добавляем недостающие поля
        if self.data:
            for key in self.data.keys():
                if key.startswith("discipline_name_") and key not in self.fields:
                    index = key.split("discipline_name_")[-1]
                    self.fields[f"discipline_name_{index}"] = forms.CharField(
                        initial=self.data.get(f"discipline_name_{index}"),
                        label=f"Новая дисциплина №{index}",
                        required=True
                    )
                    self.fields[f"discipline_code_{index}"] = forms.CharField(
                        initial=self.data.get(f"discipline_code_{index}"),
                        label=f"Новый код дисциплины №{index}",
                        required=True
                    )
                    for sem in range(1, 9):
                        self.fields[f"discipline_semester_{sem}_{index}"] = forms.IntegerField(
                            initial=self.data.get(f"discipline_semester_{sem}_{index}", 0),
                            label=f"Семестр {sem}",
                            required=False
                        )
        disciplines_data = []
        for field_name, field in self.fields.items():
            if field_name.startswith('discipline_id_'):
                index = field_name[len('discipline_id_'):]
                discipline = {
                    'id': self.data.get(f'discipline_id_{index}'),
                    'name': self.data.get(f'discipline_name_{index}'),
                    'code': self.data.get(f'discipline_code_{index}'),
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

        # 1. Сохранение Curriculum
        curriculum_data = data_objects["curriculum"][0]
        restored_curriculum = Curriculum.from_dict(curriculum_data)

        # Обновление полей curriculum
        if admission_year := self.data.get("admission_year"):
            restored_curriculum.admission_year = admission_year
        if qualification_name := self.data.get("qualification_name"):
            if hasattr(restored_curriculum, "qualification") and isinstance(restored_curriculum.qualification, dict):
                restored_curriculum.qualification.name = qualification_name

        restored_curriculum.save()

        # 2. Сохранение Categories с bulk_create
        categories_data = data_objects.get("categories", [])
        restored_categories = [
            Category(
                identificator=cat_data["identificator"],
                cycles=cat_data["cycles"],
                curriculum=restored_curriculum,
                warnings=cat_data["warnings"],
                warning_description=cat_data["warning_description"]
            )
            for cat_data in categories_data
        ]
        Category.objects.bulk_create(restored_categories)

        # Создаем словарь для быстрого поиска категорий по identificator
        categories_dict = {cat.identificator: cat for cat in restored_categories}

        # 3. Сохранение StudyCycles с bulk_create
        study_cycles_data = data_objects.get("study_cycles", [])
        restored_study_cycles = [
            StudyCycle(
                identificator=sc_data["identificator"],
                cycles=sc_data["cycles"],
                categories=categories_dict.get(sc_data["categories"]["identificator"]),
                warnings=sc_data["warnings"],
                warning_description=sc_data["warning_description"]
            )
            for sc_data in study_cycles_data
        ]
        StudyCycle.objects.bulk_create(restored_study_cycles)

        # Словарь для быстрого поиска циклов по identificator
        study_cycles_dict = {sc.identificator: sc for sc in restored_study_cycles}

        # 4. Сохранение Modules с bulk_create
        modules_data = data_objects.get("modules", [])
        restored_modules = [
            Module(
                name=m_data["module_name"],
                code_of_discipline=m_data["code_of_discipline"],
                code_of_cycle_block=m_data["code_of_cycle_block"],
                study_cycles=study_cycles_dict.get(m_data["study_cycles"]["identificator"])
            )
            for m_data in modules_data
        ]
        Module.objects.bulk_create(restored_modules)

        # Словарь для быстрого поиска модулей по имени
        modules_dict = {m.name: m for m in restored_modules}

        # 5. Сохранение Disciplines
        disciplines_data = data_objects.get("disciplines", [])
        existing_disciplines = Discipline.objects.filter(
            name__in=[d['name'] for d in disciplines_data],
            code__in=[d['code'] for d in disciplines_data]
        ).select_related('specialty')

        # Словарь существующих дисциплин для быстрого поиска
        existing_disciplines_dict = {(d.name, d.code): d for d in existing_disciplines}

        disciplines_to_create = []
        restored_disciplines = []

        for d_data in disciplines_data:
            key = (d_data['name'], d_data['code'])
            if key in existing_disciplines_dict:
                discipline = existing_disciplines_dict[key]
            else:
                discipline = Discipline(
                    code=d_data["code"],
                    name=d_data["name"],
                    specialty=Specialty.from_dict(d_data["specialty"]),
                )
                disciplines_to_create.append(discipline)

            restored_disciplines.append(discipline)

        # Массовое создание новых дисциплин
        if disciplines_to_create:
            Discipline.objects.bulk_create(disciplines_to_create)

        # Подготовка данных для связей many-to-many
        discipline_module_relations = []
        discipline_cycle_relations = []

        for d_data, discipline in zip(disciplines_data, restored_disciplines):
            module_name = d_data["module"]["module_name"] if d_data["module"] else None
            if module_name and module_name in modules_dict:
                discipline_module_relations.append(
                    Discipline.modules.through(
                        discipline_id=discipline.id,
                        module_id=modules_dict[module_name].id
                    )
                )

            cycle_relation = d_data["cycle_relation"]
            for sc in restored_study_cycles:
                if sc.cycles == cycle_relation:
                    discipline_cycle_relations.append(
                        Discipline.study_cycles.through(
                            discipline_id=discipline.id,
                            studycycle_id=sc.id
                        )
                    )

        # Массовое создание связей many-to-many
        if discipline_module_relations:
            Discipline.modules.through.objects.bulk_create(discipline_module_relations)

        if discipline_cycle_relations:
            Discipline.study_cycles.through.objects.bulk_create(discipline_cycle_relations)

        # 6. Сохранение ClockCells с bulk_create
        clock_cells_data = data_objects.get("clock_cells", [])
        clock_cells_to_create = []

        # Словарь для быстрого поиска дисциплин
        disciplines_dict = {f"{d.code}.{d.name}": d for d in restored_disciplines}

        for cc_data in clock_cells_data:
            module_name = cc_data["module"]["module_name"] if cc_data["module"] else None
            module = modules_dict.get(module_name) if module_name else None
            discipline = disciplines_dict.get(cc_data["discipline"])

            clock_cell = ClockCell(
                code_of_type_work=cc_data["code_of_type_work"],
                code_of_type_hours=cc_data["code_of_type_hours"],
                course=cc_data["course"],
                term=cc_data["term"],
                count_of_clocks=cc_data["count_of_clocks"],
                module=module,
                discipline=discipline,
                curriculum=restored_curriculum,
            )

            # Проверка на существование будет выполнена на уровне базы данных
            clock_cells_to_create.append(clock_cell)

        # Используем ignore_conflicts=True для пропуска дубликатов
        ClockCell.objects.bulk_create(clock_cells_to_create, ignore_conflicts=True)
