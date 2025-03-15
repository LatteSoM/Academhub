import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element
from typing import List
import json
import uuid


class RUP_parser:
    def __init__(self, filename: str = "rup.xml"):

        self.tree = et.parse(filename)
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
                    if child.attrib.get('КодРодителя'):
                        self.plany_stroky_childs.append(child)
                    else:
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

    def make_cycles(self):
        for cicl in self.plany_ciclov:
            self.plan_dict.append({
                "id": cicl.get('Код'),
                "identificator": cicl.get('Идентификатор'),
                "cycles": cicl.get('Цикл'),
                "children": []
            })

    def make_children_cycles(self):
        for child in self.plany_ciclov_childs:
            parent_code = child.get("КодРодителя")
            for parent in self.plan_dict:
                if parent_code == parent['id']:
                    parent['children'].append({
                        "id": child.get('Код'),
                        "identificator": child.get('Идентификатор'),
                        "cycles": child.get('Цикл'),
                        "parent_id": child.get('КодРодителя'),
                        "plans_of_string": []
                    })

    def get_clock_cells(self, child_object, child_code_xml):

        true_type_of_works = ['Итого часов', 'Лекционные занятия', 'Практические занятия', 'Самостоятельная работа', 'Часы на контроль', 'Курсовое проектирование']
        for hour in self.plany_novie_chasy:
            new_hour_parent_id = hour.get("КодОбъекта")

            code_of_type_work = self.spravochnik_vidy_rabot.get(hour.get("КодВидаРаботы"))
            code_of_type_hourse = self.spravochnik_tipa_chasov.get((hour.get("КодТипаЧасов")))

            if new_hour_parent_id == child_code_xml and int(hour.get("Количество")) > 1:
                if code_of_type_hourse == 'Часы в объемных показателях' and code_of_type_work in true_type_of_works:
                    course = int(hour.get("Курс"))
                    term = int(hour.get("Семестр"))
                    child_object['clock_cells'][course]['terms'][term - 1]['clock_cells'].append({
                        'id': str(uuid.uuid4()),
                        'code_of_type_work': code_of_type_work,
                        'code_of_type_hours': code_of_type_hourse,
                        'course': int(course),
                        'term': int(term),
                        'count_of_clocks': int(hour.get("Количество")),
                        'parent_string_id': child_object['id']
                    })


    def generate_courses_array(self):
        courses = []

        for i in range(1, 5):
            course_object = {
                'id': str(uuid.uuid4()),
                'course_number': i,
                'terms': []
            }

            for j in range(1, 3):
                term_object = {
                    'id': str(uuid.uuid4()),
                    'term_number': j,
                    'clock_cells': []
                }

                course_object['terms'].append(term_object)

            courses.append(course_object)
        
        print(courses)
        return courses
            

    def get_parent_strings_with_hours(self):
        for cycl in self.plan_dict:
            cycl['id'] = str(uuid.uuid4())

            for child in cycl['children']:
                child_id_local = child['id']
                child['id'] = str(uuid.uuid4())
                child['parent_id'] = cycl['id']

                for string in self.plany_stroky:
                    string_block_id = string.get("КодБлока")
                    if child_id_local == string_block_id:
                        parent_string_id_local = string.get('Код')
                        parent_string_object = {
                            'id': str(uuid.uuid4()),
                            'discipline': string.get('Дисциплина'),
                            'code_of_discipline': string.get('ДисциплинаКод'),
                            'code_of_cycle_block': child['id'],
                            'clock_cells': self.generate_courses_array(),
                            'children_strings': []
                        }

                        for child_string in self.plany_stroky_childs:
                            code_of_parent = child_string.get('КодРодителя')
                            if parent_string_id_local == code_of_parent:
                                child_string_id_local = child_string.get('Код')
                                child_string_object = {
                                    'id': str(uuid.uuid4()),
                                    'discipline': child_string.get('Дисциплина'),
                                    'code_of_discipline': child_string.get('ДисциплинаКод'),
                                    'code_of_cycle_block': child['id'],
                                    'parent_string_id': parent_string_object['id'],
                                    'clock_cells': self.generate_courses_array(),
                                }
                                
                                self.get_clock_cells(child_string_object, child_string_id_local)

                                parent_string_object['children_strings'].append(child_string_object)


                        self.get_clock_cells(parent_string_object, parent_string_id_local)

                        child['plans_of_string'].append(parent_string_object)


    def get_plan(self):
        self.get_elements_from_file()
        self.make_cycles()
        self.make_children_cycles()
        self.get_parent_strings_with_hours()

        self.rup['stady_plan'] = self.plan_dict

        with open("plan.json", "w", encoding="utf-8") as file:
            json.dump(self.rup, file, ensure_ascii=False, indent=4)
        print("=== JSON data (from XML) ===")
        return self.plan_dict
