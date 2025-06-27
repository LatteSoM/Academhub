import unittest

from Curriculum.parser_for_plx import RUP_parser


class TestRUPParserInvalidData(unittest.TestCase):

    def setUp(self):
        self.parser = RUP_parser()
        self.incomplete_file_path = 'data/incomplete_plan.plx'


    def test_handle_incomplete_data(self):
        self.parser.add_file(self.incomplete_file_path)
        self.parser.get_elements_from_file()

        self.assertEqual(len(self.parser.plany_ciclov), 0)
        self.assertEqual(len(self.parser.plany_ciclov_childs), 0)
        self.assertEqual(len(self.parser.plany_stroky), 0)
        self.assertEqual(len(self.parser.plany_novie_chasy), 0)
        self.assertEqual(len(self.parser.spravochnik_vidy_rabot), 0)
        self.assertEqual(len(self.parser.spravochnik_tipa_chasov), 0)
        self.assertEqual(len(self.parser.spravochnik_tipa_objecta), 0)