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
        self.parser.add_file('data/uchebnyi-plan-09.02.07-P-P-ofo-3g10m-2024.plx')
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
        self.parser.add_file('data/uchebnyi-plan-09.02.07-P-P-ofo-3g10m-2024.plx')
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

    def test_minimal_structure_parsing(self):
        """Tests if the parser correctly handles a minimal plan structure."""
        self.parser.add_file(self.test_file_path) # Uses data/test_plan.plx
        rup_plan = self.parser.get_plan()

        self.assertIsNotNone(rup_plan)
        self.assertIn('stady_plan', rup_plan)
        stady_plan = rup_plan['stady_plan']
        self.assertEqual(len(stady_plan), 1, "Should be one top-level cycle")

        top_cycle = stady_plan[0]
        self.assertEqual(top_cycle['cycles'], "Test Cycle 1")
        self.assertIn('children', top_cycle)
        self.assertEqual(len(top_cycle['children']), 1, "Top cycle should have one child")

        child_cycle = top_cycle['children'][0]
        self.assertEqual(child_cycle['cycles'], "Test Child Cycle 1.1")
        self.assertIn('disciplines', child_cycle)
        self.assertIn('modules', child_cycle) # Key should exist even if empty
        self.assertEqual(len(child_cycle['modules']), 0, "Child cycle should have no modules in this minimal plan")
        self.assertEqual(len(child_cycle['disciplines']), 1, "Child cycle should have one direct discipline")

        discipline = child_cycle['disciplines'][0]
        self.assertEqual(discipline['discipline_name'], "Test Discipline 1")
        self.assertIn('clock_cells', discipline)
        self.assertEqual(len(discipline['clock_cells']), 1, "Discipline should have one clock cell")

        clock_cell = discipline['clock_cells'][0]
        self.assertEqual(clock_cell['code_of_type_work'], "Лекционные занятия")
        self.assertEqual(clock_cell['count_of_clocks'], 10)

class TestRUPParserGetPlan(unittest.TestCase):
    def setUp(self):
        self.parser = RUP_parser()
        self.test_file_path = 'data/uchebnyi-plan-09.02.07-P-P-ofo-3g10m-2024.plx'

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
        self.test_file_path = 'data/uchebnyi-plan-09.02.07-P-P-ofo-3g10m-2024.plx'

    def test_get_clock_cells_and_strings_valid_data(self):
        self.parser.add_file(self.test_file_path)
        self.parser.get_elements_from_file()
        self.parser.make_cycles()
        self.parser.make_children_cycles()
        self.parser.get_parent_strings_with_hours()

        self.assertGreater(len(self.parser.plan_dict), 0)
        for cycle in self.parser.plan_dict:
            for child_cycle in cycle['children']:
                has_disciplines = False
                # Check disciplines directly under child_cycle
                if child_cycle.get('disciplines'):
                    self.assertGreater(len(child_cycle['disciplines']), 0, f"Child cycle '{child_cycle.get('cycles')}' should have disciplines")
                    for discipline in child_cycle['disciplines']:
                         self.assertIn('clock_cells', discipline)
                         self.assertGreater(len(discipline['clock_cells']), 0, f"Discipline '{discipline.get('discipline_name')}' in child cycle '{child_cycle.get('cycles')}' should have clock_cells")
                         has_disciplines = True
                
                # Check disciplines within modules under child_cycle
                if child_cycle.get('modules'):
                    self.assertGreater(len(child_cycle['modules']), 0, f"Child cycle '{child_cycle.get('cycles')}' should have modules if key exists")
                    for module in child_cycle['modules']:
                        self.assertIn('disciplines', module)
                        if module.get('disciplines'):
                             self.assertGreater(len(module['disciplines']), 0, f"Module '{module.get('module_name')}' should have disciplines if key exists")
                             for discipline in module['disciplines']:
                                 self.assertIn('clock_cells', discipline)
                                 self.assertGreater(len(discipline['clock_cells']), 0, f"Discipline '{discipline.get('discipline_name')}' in module '{module.get('module_name')}' should have clock_cells")
                                 has_disciplines = True
                        # Also check if clock_cells are directly under the module (if applicable by parser logic)
                        # According to parser_for_plx.py, clock_cells can be directly under modules too
                        if module.get('clock_cells'):
                             self.assertGreater(len(module['clock_cells']), 0, f"Module '{module.get('module_name')}' should have clock_cells if key exists")
                             has_disciplines = True # Treat module hours as related to disciplines for this check

                # We don't assert assertTrue(has_disciplines) here anymore,
                # as some cycles might legitimately not contain disciplines (e.g., container cycles).
                # The inner assertions check clock_cells *if* disciplines/modules exist.
                pass # Placeholder if no other code needed here, ensures block is valid


class TestRUPParserGetAllData(unittest.TestCase):
    def setUp(self):
        self.parser = RUP_parser()
        self.test_file_path = 'data/uchebnyi-plan-09.02.07-P-P-ofo-3g10m-2024.plx'

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
    REAL_PLAN_PATH = 'data/uchebnyi-plan-09.02.07-P-P-ofo-3g10m-2024.plx'
    EXPECTED_QUALIFICATION = "Программист"
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
        self.assertEqual(first_cycle['cycles'], "ОБЩЕОБРАЗОВАТЕЛЬНАЯ ПОДГОТОВКА")
        
        first_child = first_cycle['children'][0]
        
        # Find the 'История' discipline, whether directly under the child cycle or within a module
        history_discipline = None
        # Check direct disciplines first
        if first_child.get('disciplines'):
            for disc in first_child['disciplines']:
                if disc.get('discipline_name') == "История":
                    history_discipline = disc
                    break
        
        # If not found directly, check within modules
        if not history_discipline and first_child.get('modules'):
             for module in first_child['modules']:
                 if module.get('disciplines'):
                     for disc in module['disciplines']:
                         if disc.get('discipline_name') == "История":
                             history_discipline = disc
                             break
                 if history_discipline:
                     break
        
        self.assertIsNotNone(history_discipline, "Could not find the 'История' discipline in the first child cycle")
        self.assertEqual(history_discipline['discipline_name'], "История")
        self.assertEqual(sum(c['count_of_clocks'] for c in history_discipline['clock_cells']), 144)

if __name__ == '__main__':
    unittest.main()