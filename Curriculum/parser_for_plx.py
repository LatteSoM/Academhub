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

    def add_file(self, file_path):
        # Try common encodings for XML files, especially those from Windows systems
        encodings_to_try = ['utf-8', 'cp1251', 'utf-16']
        xml_content_str = None
        detected_encoding = None

        for enc in encodings_to_try:
            try:
                with open(file_path, 'rb') as f_bytes:
                    xml_content_bytes = f_bytes.read()
                
                # Attempt decoding
                xml_content_str = xml_content_bytes.decode(enc)
                
                # Basic check if decoding looks reasonable (e.g., starts with XML declaration)
                # Remove BOM if present (especially for utf-8)
                if xml_content_str.startswith('\ufeff'):
                    xml_content_str = xml_content_str[1:]
                
                if xml_content_str.strip().startswith('<?xml'):
                    detected_encoding = enc
                    # print(f"Successfully decoded with {enc}") # Optional: for debugging
                    break # Stop trying once a successful decode happens
            except (UnicodeDecodeError, LookupError):
                # print(f"Failed to decode with {enc}") # Optional: for debugging
                continue # Try next encoding
            except Exception as e:
                # Catch other potential file reading errors
                print(f"Error reading file {file_path} with encoding {enc}: {e}")
                continue

        if xml_content_str is None:
            raise ValueError(f"Could not decode file {file_path} with any of the attempted encodings: {encodings_to_try}")

        # Parse the decoded string content
        try:
            # Use fromstring to parse the decoded string
            self.root = et.fromstring(xml_content_str)
            # Reconstruct a minimal tree if needed, although direct root access is often sufficient
            self.tree = et.ElementTree(self.root)
        except et.ParseError as e:
             raise et.ParseError(f"XML ParseError in {file_path} (detected encoding: {detected_encoding}): {e}")

        # Check the structure before accessing children
        if len(self.root) > 0 and len(self.root[0]) > 0:
             self.root_child = self.root[0][0] # This assumes the diffgram/dsMMISDB structure
        else:
             # Handle cases where the structure is different or the file is minimal/empty
             # Option 1: Raise an error if the structure is mandatory
             # raise ValueError(f"Unexpected XML structure in {file_path}. Expected root[0][0] to exist.")
             # Option 2: Set root_child to None or a sensible default and let later methods handle it
             print(f"Warning: Unexpected XML structure in {file_path}. root[0][0] not found. Proceeding cautiously.")
             self.root_child = None # Or potentially self.root[0] if dsMMISDB is the direct child


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
        
        for hour in self.plany_novie_chasy:
            new_hour_parent_id = hour.get("КодОбъекта")

            code_of_type_work = self.spravochnik_vidy_rabot.get(hour.get("КодВидаРаботы"))
            code_of_type_hourse = self.spravochnik_tipa_chasov.get((hour.get("КодТипаЧасов")))

            if new_hour_parent_id == child_code_xml and int(hour.get("Количество")):
                if code_of_type_hourse == 'Часы в объемных показателях':
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
