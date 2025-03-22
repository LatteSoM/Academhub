import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element
from typing import List
import json
import uuid
import _io


__all__ = (
    'RUP_parser'
)

class RUP_parser:

    def add_file(self, file):
        self.tree = et.parse(file)
        self.root = self.tree.getroot()
        self.root_child = self.root[0][0]

        self.plan_dict = []
        self.rup = {}

        self.plany_ciclov: List[Element] = []
        self.plany_ciclov_childs: List[Element] = []
        self.plany_novie_chasy: List[Element] = []
        self.plany_stroky: List[Element] = []
        self.plany_stroky_childs: List[Element] = []
        self.spravochnik_vidy_rabot: dict = {}
        self.spravochnik_tipa_chasov: dict = {}
        self.spravochnik_tipa_objecta: dict = {}

    def get_elements_from_file(self):
        for child in self.root_child:
            tag_name = child.tag.replace("{http://tempuri.org/dsMMISDB.xsd}", '')
            match tag_name:
                case "ПланыЦиклы":
                    if child.attrib.get('КодРодителя'):
                        self.plany_ciclov_childs.append(child)
                    else:
                        self.plany_ciclov.append(child)
                case "ПланыСтроки":
                    self.plany_stroky.append(child)
                case "ПланыНовыеЧасы":
                    self.plany_novie_chasy.append(child)
                case "Планы":
                    self.rup = {
                        'id': str(uuid.uuid4()),
                        'qualification': child.get('Квалификация'),
                        'admission_year': child.get('ГодНачалаПодготовки'),
                        'stady_plan': []
                    }
                case "СправочникВидыРабот":
                    self.spravochnik_vidy_rabot[child.attrib.get('Код')] = child.attrib.get('Название')
                case "СправочникТипаЧасов":
                    self.spravochnik_tipa_chasov[child.attrib.get('Код')] = child.attrib.get('Наименование')
                case "СправочникТипОбъекта":
                    self.spravochnik_tipa_objecta[child.attrib.get('Код')] = child.attrib.get('Название')

    def make_cycles(self):
        for cicl in self.plany_ciclov:
            self.plan_dict.append({
                "id": str(uuid.uuid4()),
                "identificator": cicl.get('Идентификатор'),
                "cycles": cicl.get('Цикл'),
                "cycle_id_local": cicl.get("Код"),
                "children": []
            })

    def make_children_cycles(self):
        for child in self.plany_ciclov_childs:
            parent_code = child.get("КодРодителя")
            for parent in self.plan_dict:
                if parent_code == parent['cycle_id_local']:
                    parent['children'].append({
                        "id": str(uuid.uuid4()),
                        "identificator": child.get('Идентификатор'),
                        "cycles": child.get('Цикл'),
                        "parent_id": child.get('КодРодителя'),
                        "cycle_id_local": child.get("Код"),
                        "modules": [],
                        "disciplines": [],
                    })

    def get_clock_cells(self, child_object, child_code_xml):

        true_type_of_works = {
            'Итого часов',
            'Лекционные занятия',
            'Практические занятия',
            'Самостоятельная работа',
            'Курсовое проектирование',
            'Экзамен',
            'Зачет',
            'Зачет с оценкой',
            'Курсовой проект',
            'Курсовая работа',
            'Контрольная работа',
            'Контрольная работа',
            'Домашняя контрольная работа',
            'Оценка',
            'Эссе',
            'Реферат',
            'Расчетно-графическая работа',
            'Другие формы контроля',
        }
        for hour in self.plany_novie_chasy:
            new_hour_parent_id = hour.get("КодОбъекта")

            code_of_type_work = self.spravochnik_vidy_rabot.get(hour.get("КодВидаРаботы"))
            code_of_type_hourse = self.spravochnik_tipa_chasov.get((hour.get("КодТипаЧасов")))

            if new_hour_parent_id == child_code_xml and int(hour.get("Количество")):
                if code_of_type_hourse == 'Часы в объемных показателях' and code_of_type_work in true_type_of_works:
                    course = int(hour.get("Курс"))
                    term = int(hour.get("Семестр"))
                    if child_object.get('module_name'):
                        child_object['clock_cells'].append({
                            'id': str(uuid.uuid4()),
                            'code_of_type_work': code_of_type_work,
                            'code_of_type_hours': code_of_type_hourse,
                            'course': int(course),
                            'term': int(term),
                            'count_of_clocks': int(hour.get("Количество")),
                            'module': child_object.get('module_name'),
                            'discipline': None,
                        })

                    else:
                        child_object['clock_cells'].append({
                            'id': str(uuid.uuid4()),
                            'code_of_type_work': code_of_type_work,
                            'code_of_type_hours': code_of_type_hourse,
                            'course': int(course),
                            'term': int(term),
                            'count_of_clocks': int(hour.get("Количество")),
                            'module': None,
                            'discipline': child_object.get('discipline_name'),
                        })

    def get_parent_strings_with_hours(self):
        for cycl in self.plan_dict:
            cycl['id'] = str(uuid.uuid4())

            for child in cycl['children']:
                child_id_local = child['cycle_id_local']
                child['parent_id'] = cycl['id']

                for string in self.plany_stroky:
                    string_cycle_id_local = string.get("КодБлока")
                    if child_id_local == string_cycle_id_local:
                        parent_string_id_local = string.get('Код')
                        string_object_type = self.spravochnik_tipa_objecta.get(string.get('ТипОбъекта'))

                        if string_object_type == "Модули":
                            module = {
                                'id': str(uuid.uuid4()),
                                'module_name': string.get('Дисциплина'),
                                'code_of_discipline': string.get('ДисциплинаКод'),
                                'code_of_cycle_block': child['id'],
                                'module_local_code': parent_string_id_local,
                                'clock_cells': [],
                                'disciplines': []
                            }

                            self.get_clock_cells(module, parent_string_id_local)

                            child['modules'].append(module)

                        else:
                            string_parent_code = string.get('КодРодителя')
                            if string_parent_code:
                                for module in child['modules']:
                                    if module.get('module_local_code') == string_parent_code:
                                        discipline = {
                                            'id': str(uuid.uuid4()),
                                            'discipline_name': string.get('Дисциплина'),
                                            'code_of_discipline': string.get('ДисциплинаКод'),
                                            'code_of_cycle_block': child['id'],
                                            'module_relation': module.get('module_name'),
                                            'clock_cells': [],
                                        }

                                        self.get_clock_cells(discipline, string.get('Код'))

                                        module['disciplines'].append(discipline)

                            else:
                                discipline = {
                                    'id': str(uuid.uuid4()),
                                    'discipline_name': string.get('Дисциплина'),
                                    'code_of_discipline': string.get('ДисциплинаКод'),
                                    'code_of_cycle_block': child['id'],
                                    'cycle_relation': child.get('cycles'),
                                    'clock_cells': [],
                                }

                                self.get_clock_cells(discipline, string.get('Код'))

                                child['disciplines'].append(discipline)


    def get_plan(self):
        self.get_elements_from_file()
        self.make_cycles()
        self.make_children_cycles()
        self.get_parent_strings_with_hours()

        self.rup['stady_plan'] = self.plan_dict

        # with open(f"./Curriculum/media/plan_{self.rup['id']}.json", "w", encoding="utf-8") as file:
        #     json.dump(self.rup, file, ensure_ascii=False, indent=4)
        # # print("=== JSON data (from XML) ===")
        # # return self.plan_dict
        #
        # with open(f"./Curriculum/media/plan_{self.rup['id']}.json", "r", encoding="utf-8") as file:
        #     json_content = file.read()

        return self.rup  # Возвращаем содержимое файла в виде строки
