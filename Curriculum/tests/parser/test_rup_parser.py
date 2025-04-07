import sys
import unittest

from Curriculum.parser_for_plx import RUP_parser

class TestRUPParserAddFile(unittest.TestCase):

    def setUp(self):
        self.parser = RUP_parser()
        self.test_file_path = 'data/test_plan.plx'

    def test_add_file_valid_file(self):
        self.parser.add_file(self.test_file_path)
        self.assertIsNotNone(self.parser.tree)
        self.assertIsNotNone(self.parser.root)
        self.assertIsNotNone(self.parser.root_child)

    def test_add_file_invalid_file(self):
        invalid_path = 'data/non_existent_file.plx'
        with self.assertRaises(FileNotFoundError):
            self.parser.add_file(invalid_path)

    def test_get_elements_from_file_valid_file(self):
        self.parser.add_file(self.test_file_path)
        self.parser.get_elements_from_file()
        self.assertGreater(len(self.parser.plany_ciclov), 0)
        self.assertGreater(len(self.parser.plany_ciclov_childs), 0)
        self.assertGreater(len(self.parser.plany_stroky), 0)
        self.assertGreater(len(self.parser.plany_novie_chasy), 0)
        self.assertGreater(len(self.parser.spravochnik_vidy_rabot), 0)
        self.assertGreater(len(self.parser.spravochnik_tipa_chasov), 0)
        self.assertGreater(len(self.parser.spravochnik_tipa_objecta), 0)

    def test_make_children_cycles_valid_data(self):
        self.parser.add_file('Curriculum/tests/data/parser/test_plan_elements.plx')
        self.parser.get_elements_from_file()
        self.parser.make_cycles()
        self.parser.make_children_cycles()

        self.assertGreater(len(self.parser.plan_dict), 0)
        for cycle in self.parser.plan_dict:
            if cycle['children']:
                self.assertGreater(len(cycle['children']), 0)
                for child_cycle in cycle['children']:
                    self.assertIsInstance(child_cycle, dict)
                    self.assertIn('id', child_cycle)
                    self.assertIn('identificator', child_cycle)
                    self.assertIn('cycles', child_cycle)
                    self.assertIn('parent_id', child_cycle)
                    self.assertIn('cycle_id_local', child_cycle)
                    self.assertIn('modules', child_cycle)
                    self.assertIn('disciplines', child_cycle)
        self.assertGreater(len(self.parser.rup), 0)

    def test_make_cycles_valid_data(self):
        self.parser.add_file('Curriculum/tests/data/parser/test_plan_elements.plx')
        self.parser.get_elements_from_file()
        self.parser.make_cycles()

        self.assertGreater(len(self.parser.plan_dict), 0)
        for item in self.parser.plan_dict:
            self.assertIsInstance(item, dict)
            self.assertIn('id', item)
            self.assertIn('identificator', item)
            self.assertIn('cycles', item)
            self.assertIn('cycle_id_local', item)
            self.assertIn('children', item)

class TestRUPParserGetPlan(unittest.TestCase):
    def setUp(self):
        self.parser = RUP_parser()
        self.test_file_path = 'Curriculum/tests/data/parser/test_plan_elements.plx'

    def test_get_plan_valid_file(self):
        self.parser.add_file(self.test_file_path)
        rup_plan = self.parser.get_plan()
        self.assertIsNotNone(rup_plan)
        self.assertIsInstance(rup_plan, dict)
        self.assertIn('id', rup_plan)
        self.assertIn('qualification', rup_plan)
        self.assertIn('admission_year', rup_plan)
        self.assertIn('stady_plan', rup_plan)
        self.assertIsInstance(rup_plan['stady_plan'], list)
        self.assertGreater(len(rup_plan['stady_plan']), 0)

class TestRUPParserClockCellsAndStrings(unittest.TestCase):
    def setUp(self):
        self.parser = RUP_parser()
        self.test_file_path = 'Curriculum/tests/data/parser/test_plan_elements.plx'

    def test_get_clock_cells_and_strings_valid_data(self):
        self.parser.add_file(self.test_file_path)
        self.parser.get_elements_from_file()
        self.parser.make_cycles()
        self.parser.make_children_cycles()
        self.parser.get_parent_strings_with_hours()

        self.assertGreater(len(self.parser.plan_dict), 0)
        for cycle in self.parser.plan_dict:
            for child_cycle in cycle['children']:
                self.assertGreater(len(child_cycle['modules']), 0)
                for module in child_cycle['modules']:
                    self.assertGreater(len(module['disciplines']), 0)
                    for discipline in module['disciplines']:
                        self.assertGreater(len(discipline['clock_cells']), 0)

class TestRUPParserGetAllData(unittest.TestCase):
    def setUp(self):
        self.parser = RUP_parser()
        self.test_file_path = 'Curriculum/tests/data/parser/test_plan_elements.plx'

    def test_get_all_data_valid_file(self):
        self.parser.add_file(self.test_file_path)
        rup_plan = self.parser.get_plan()
        self.assertIsNotNone(rup_plan)
        self.assertIsInstance(rup_plan, dict)
        self.assertIn('stady_plan', rup_plan)
        self.assertIsInstance(rup_plan['stady_plan'], list)

        for cycle in rup_plan['stady_plan']:
            self.assertIsInstance(cycle, dict)
            self.assertIn('children', cycle)
            for child_cycle in cycle['children']:
                self.assertIsInstance(child_cycle, dict)
                self.assertIn('modules', child_cycle)
                for module in child_cycle['modules']:
                    self.assertIsInstance(module, dict)
                    self.assertIn('disciplines', module)
                    for discipline in module['disciplines']:
                        self.assertIsInstance(discipline, dict)
                        self.assertIn('clock_cells', discipline)
                        for clock_cell in discipline['clock_cells']:
                            self.assertIsInstance(clock_cell, dict)
                            self.assertIn('code_of_type_work', clock_cell)
                            self.assertIn('code_of_type_hours', clock_cell)
                            self.assertIn('course', clock_cell)
                            self.assertIn('term', clock_cell)
                            self.assertIn('count_of_clocks', clock_cell)

class TestRealPlanIntegration(unittest.TestCase):
    REAL_PLAN_PATH = 'Curriculum/tests/data/uchebnyi-plan-09.02.07-P-P-ofo-3g10m-2024.plx'
    EXPECTED_QUALIFICATION = "09.02.07 Программирование в компьютерных системах"
    EXPECTED_ADMISSION_YEAR = "2024"
    
    def setUp(self):
        self.parser = RUP_parser()
        self.parser.add_file(self.REAL_PLAN_PATH)
        self.parsed_data = self.parser.get_plan()

    def test_basic_structure(self):
        self.assertEqual(self.parsed_data['qualification'], self.EXPECTED_QUALIFICATION)
        self.assertEqual(self.parsed_data['admission_year'], self.EXPECTED_ADMISSION_YEAR)
        self.assertIsInstance(self.parsed_data['stady_plan'], list)
        self.assertGreater(len(self.parsed_data['stady_plan']), 0)

    def test_cycles_hierarchy(self):
        for cycle in self.parsed_data['stady_plan']:
            self.assertIn('children', cycle)
            for child_cycle in cycle['children']:
                self.assertIn('modules', child_cycle)
                self.assertIn('disciplines', child_cycle)
                
                for module in child_cycle['modules']:
                    self.assertIn('disciplines', module)
                    self.assertIn('clock_cells', module)
                    
                    for discipline in module['disciplines']:
                        self.assertGreater(len(discipline['clock_cells']), 0)

    def test_clock_cells_integrity(self):
        total_hours = 0
        for cycle in self.parsed_data['stady_plan']:
            for child_cycle in cycle['children']:
                for module in child_cycle['modules']:
                    for discipline in module['disciplines']:
                        for clock in discipline['clock_cells']:
                            self.assertIsInstance(clock['count_of_clocks'], int)
                            self.assertGreaterEqual(clock['count_of_clocks'], 0)
                            total_hours += clock['count_of_clocks']
        
        self.assertGreater(total_hours, 5000)

    def test_actual_data_validation(self):
        first_cycle = self.parsed_data['stady_plan'][0]
        self.assertEqual(first_cycle['cycles'], "Общий гуманитарный и социально-экономический цикл")
        
        first_child = first_cycle['children'][0]
        self.assertGreaterEqual(len(first_child['modules'][0]['disciplines']), 3)
        
        history_discipline = first_child['modules'][0]['disciplines'][0]
        self.assertEqual(history_discipline['discipline_name'], "История")
        self.assertEqual(sum(c['count_of_clocks'] for c in history_discipline['clock_cells']), 144)

if __name__ == '__main__':
    unittest.main()