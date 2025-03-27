import json
from collections import defaultdict

from django import forms

from Academhub.models import Specialty, Category, Curriculum, StudyCycle, Module, Discipline, \
    ClockCell


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
            disc_code = discipline_data.get('code')
            # Генерация дополнительных полей для 8 семестров
            for semester in range(1, 9):
                field_name = f'discipline_semester_{semester}_{i}'

                # Получаем часы из clock_cell_lookup, если они есть
                initial_value = clock_cell_lookup.get(f"{disc_code}.{disc_name}", {}).get(semester, 0)

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

            prompt = Discipline.objects.filter(name=discipline_data['name'], code=discipline_data['code'])
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
            discipline = next((d for d in restored_disciplines if f"{d.code}.{d.name}" == cc_data["discipline"]), None)

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

            if not ClockCell.objects.filter(
                code_of_type_work=clock_cell_obj.code_of_type_work,
                code_of_type_hours=clock_cell_obj.code_of_type_hours,
                course=clock_cell_obj.course,
                term=clock_cell_obj.term,
                count_of_clocks=clock_cell_obj.count_of_clocks,
                module=clock_cell_obj.module,
                discipline=clock_cell_obj.discipline,
                curriculum=clock_cell_obj.curriculum,
                                        ) :

                clock_cell_obj.save()
                restored_clock_cells.append(clock_cell_obj)