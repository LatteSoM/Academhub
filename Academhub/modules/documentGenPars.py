import os
import sys
import django

from openpyxl import Workbook
from openpyxl.styles import Color, PatternFill

# Определение среды Django для тестов
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Academhub.settings")
django.setup()
from Academhub.models import GroupStudents, Qualification, Specialty, Student


class GroupTableGenerator:
    """
    Класс для генерации таблицы групп
    """ 
    def __init__(self, groups) -> None:
        """
        Принимает на вход список групп

        groups: list[GroupStudents]
        """
        self.groups = groups

    def generate_document(self, path: str) -> None:
        """
        Генерирует новый документ по указанному пути
        """
        workbook = Workbook()
        worksheet = workbook.active
        if worksheet is not None:
            worksheet.title = "Группы"
            # Заголовки
            worksheet["A1"] = "№"
            worksheet["B1"] = "1 курс (9 кл.)"
            worksheet["C1"] = "2 курс (9 кл.)"
            worksheet["D1"] = "1 курс (11 кл.)"
            worksheet["E1"] = "3 курс (9 кл.)"
            worksheet["F1"] = "2 курс (11 кл.)"
            worksheet["G1"] = "4 курс (9 кл.)"
            worksheet["H1"] = "3 курс (11 кл.)"

            # Ширина ячеек
            worksheet.column_dimensions['A'].width = len(str(len(self.groups))) + 3
            GROUPNAME_CELL_WIDTH = max([len(str(i.number)) for i in self.groups])
            worksheet.column_dimensions['B'].width = GROUPNAME_CELL_WIDTH
            worksheet.column_dimensions['C'].width = GROUPNAME_CELL_WIDTH
            worksheet.column_dimensions['D'].width = GROUPNAME_CELL_WIDTH
            worksheet.column_dimensions['E'].width = GROUPNAME_CELL_WIDTH
            worksheet.column_dimensions['F'].width = GROUPNAME_CELL_WIDTH
            worksheet.column_dimensions['G'].width = GROUPNAME_CELL_WIDTH
            worksheet.column_dimensions['H'].width = GROUPNAME_CELL_WIDTH

            for i in range(len(self.groups)):
                column_letter = 0
                match self.groups[i].current_course:
                    case 1:
                        if self.groups[i].education_base == "Основное общее":
                            column_letter = 2
                        elif self.groups[i].education_base == "Среднее общее":
                            column_letter = 4
                    case 2:
                        if self.groups[i].education_base == "Основное общее":
                            column_letter = 3
                        elif self.groups[i].education_base == "Среднее общее":
                            column_letter = 6
                    case 3:
                        if self.groups[i].education_base == "Основное общее":
                            column_letter = 5
                        elif self.groups[i].education_base == "Среднее общее":
                            column_letter = 8
                    case 4:
                        column_letter = 7
                
                last_row = worksheet.max_row
                while last_row > 0 and worksheet.cell(row=last_row, column=column_letter).value is None:
                    last_row -= 1
                
                worksheet.cell(row=last_row+1, column=column_letter).value = self.groups[i].number

            for i in range(2, worksheet.max_row+1):
                worksheet.cell(row=i, column=1).value = i - 1
            
            workbook.save(path)

class CourseDifferenceError(Exception):
    def __init__(self, message="Для формирования таблицы, студенты должны быть с одного курса"):
        self.message = message
        super().__init__(self.message)

class EducationBaseDifferenceError(Exception):
    def __init__(self, message="Для формирования таблицы, студенты должны быть с одинаковой базой образования"):
        self.message = message
        super().__init__(self.message)

class CourseTableGenerator:
    """
    Класс для генерации таблицы курса
    """
    def __init__(self, students) -> None:
        """
        Принимает на вход список со студентами у которых
        указан одинаковый курс

        students: list[Student]
        """
        if not all(student.group.current_course == students[0].group.current_course for student in students):
            raise CourseDifferenceError
        if not all(student.group.education_base == students[0].group.education_base for student in students):
            raise EducationBaseDifferenceError
        
        self.students = students
        self.course = students[0].group.current_course
        if students[0].group.education_base == "Основное общее":
            self.education_base = "9 кл."
        elif students[0].group.education_base == "Среднее общее":
            self.education_base = "11 кл."

    def generate_document(self, path: str) -> None:
        """
        Генерирует новый документ по указанному пути
        """
        workbook = Workbook()
        worksheet = workbook.active
        
        if worksheet is not None:
            worksheet.title = f"{self.course} курс ({self.education_base})"

            # Заголовки
            worksheet["A1"] = "№"
            worksheet["B1"] = "ФИО"
            worksheet["C1"] = "Дата рождения"
            worksheet["D1"] = "Специальность"
            worksheet["E1"] = "Группа"
            worksheet["F1"] = "База образования (9 или 11 классов)"
            worksheet["G1"] = "Основа образования (бюджет, внебюджет)"
            worksheet["H1"] = "Приказ о зачислении"
            worksheet["I1"] = "Переводной приказ на 2 курс"
            worksheet["J1"] = "Переводной приказ на 3 курс"
            worksheet["K1"] = "Переводной приказ на 4 курс"
            worksheet["L1"] = "Отчисление в связи с окончанием обучения"
            worksheet["M1"] = "Примечание"
            worksheet["N1"] = "Телефон"

            # Высота ячеек
            worksheet.row_dimensions[1].height = 40

            # Ширина ячеек
            worksheet.column_dimensions['A'].width = len(str(len(self.students))) + 3
            worksheet.column_dimensions['B'].width = max([len(i.full_name) for i in self.students]) + 3
            worksheet.column_dimensions['C'].width = max([len(str(i.birth_date)) for i in self.students]) + 3
            worksheet.column_dimensions['D'].width = max([len(i.group.qualification.specialty.code) for i in self.students]) + 3
            worksheet.column_dimensions['E'].width = max([len(i.group.number) for i in self.students]) + 3
            worksheet.column_dimensions['F'].width = max([len(i.group.education_base) for i in self.students]) + 3
            worksheet.column_dimensions['G'].width = max([len(i.education_basis) for i in self.students]) + 3
            worksheet.column_dimensions['H'].width = max([len(i.admission_order) for i in self.students]) + 3
            worksheet.column_dimensions['I'].width = max([len(str(i.transfer_to_2nd_year_order)) for i in self.students]) + 3
            worksheet.column_dimensions['J'].width = max([len(str(i.transfer_to_3rd_year_order)) for i in self.students]) + 3
            worksheet.column_dimensions['K'].width = max([len(str(i.transfer_to_4th_year_order)) for i in self.students]) + 3
            worksheet.column_dimensions['L'].width = max([len(str(i.expelled_due_to_graduation)) for i in self.students]) + 3
            worksheet.column_dimensions['M'].width = max([len(str(i.note)) for i in self.students]) + 3
            worksheet.column_dimensions['N'].width = max([len(i.phone) for i in self.students]) + 3

            for i in range(len(self.students)):
                worksheet.cell(row=i+2, column=1).value = i+1
                worksheet.cell(row=i+2, column=2).value = self.students[i].full_name
                worksheet.cell(row=i+2, column=3).value = self.students[i].birth_date
                worksheet.cell(row=i+2, column=4).value = self.students[i].group.qualification.specialty.code
                worksheet.cell(row=i+2, column=5).value = self.students[i].group.number
                worksheet.cell(row=i+2, column=6).value = self.students[i].group.education_base
                worksheet.cell(row=i+2, column=7).value = self.students[i].education_basis
                worksheet.cell(row=i+2, column=8).value = self.students[i].admission_order
                worksheet.cell(row=i+2, column=9).value = self.students[i].transfer_to_2nd_year_order
                worksheet.cell(row=i+2, column=10).value = self.students[i].transfer_to_3rd_year_order
                worksheet.cell(row=i+2, column=11).value = self.students[i].transfer_to_4th_year_order
                worksheet.cell(row=i+2, column=12).value = self.students[i].expelled_due_to_graduation
                worksheet.cell(row=i+2, column=13).value = self.students[i].note
                worksheet.cell(row=i+2, column=14).value = self.students[i].phone
            
            workbook.save(path)

class StatisticsTableGenerator:
    def __init__(self, specialties, qualifications, students) -> None:
        self.specialties = specialties
        self.qualifications = qualifications
        self.students = students

    def generate_document(self, path):
        workbook = Workbook()
        worksheet = workbook.active

        if worksheet is not None:
            from datetime import date
            today = date.today()
            worksheet.title = f"Статистика ({today.day}.{today.month}.{today.year})"
            
            # Заголовки (первый ряд)
            worksheet["A1"] = "№ п/п"
            worksheet["B1"] = "Код"
            worksheet["C1"] = "Направление подготовки/специальности"
            worksheet["D1"] = "Профиль (направленность/ специализация), квалификация для программ СПО"
            worksheet["E1"] = "Форма обучения"
            worksheet["F1"] = "Вид обучения"
            worksheet.merge_cells("G1:R1")
            worksheet["G1"] = "Контингент"
            
            # Заголовки (второй ряд)
            worksheet["A2"] = 1
            worksheet["B2"] = 2
            worksheet["C2"] = 3
            worksheet["D2"] = 4
            worksheet["E2"] = 5
            worksheet["F2"] = 6
            worksheet.merge_cells("G2:J2")
            worksheet["G2"] = 7
            worksheet.merge_cells("K2:M2")
            worksheet["K2"] = 8
            worksheet.merge_cells("N2:Q2")
            worksheet["N2"] = 9
            worksheet["R2"] = 10

            # Заголовки (третий ряд)
            worksheet["A3"] = '-'
            worksheet["B3"] = '-'
            worksheet["C3"] = '-'
            worksheet["D3"] = '-'
            worksheet["E3"] = '-'
            worksheet["F3"] = '-'
            worksheet.merge_cells("G3:J3")
            worksheet["G3"] = "9кл" 
            worksheet.merge_cells("K3:M3")
            worksheet["K3"] = "11кл" 
            worksheet.merge_cells("N3:Q3")
            worksheet["N3"] = "Акад.отпуск"
            worksheet["R3"] = "Итого"

            # Заголовки (четверый ряд)
            worksheet["G4"] = "1 курс"
            worksheet["H4"] = "2 курс"
            worksheet["I4"] = "3 курс"
            worksheet["J4"] = "4 курс"
            worksheet["K4"] = "1 курс"
            worksheet["L4"] = "2 курс"
            worksheet["M4"] = "3 курс"
            worksheet["N4"] = "1 курс"
            worksheet["O4"] = "2 курс"
            worksheet["P4"] = "3 курс"
            worksheet["Q4"] = "4 курс"
            
            entry_count = 1 # порядковый номер квалификации
            entry_index = 5 # индекс последней заполненной строки, вынесен отдельно,
            # т.к. значение его увеличения изменчиво в зависимости от объединения строк
            isip_done = False

            # Проходимся по каждой специальности каждой квалификации
            for specialty in self.specialties:
                qualifications_specialty = self.qualifications.filter(specialty__code=specialty.code)
                for qualification in qualifications_specialty:
                    # Здесь я единожды разбираюсь с 1-м курсом исипа и выделяю место под него в таблице,
                    # после чего единожды заполняю их количество, больше в этом цикле заполнения связанного с ними не будет
                    if specialty.name == "Информационные системы и программирование" and not isip_done:
                        worksheet.merge_cells(f"G{entry_index}:G{entry_index+(len(qualifications_specialty)-2)}")
                        worksheet.cell(row=entry_index, column=7).fill = PatternFill("solid", fgColor=Color(indexed=3))
                        worksheet.cell(row=entry_index, column=7).value = len(self.students.filter(group__qualification__name="Информационные системы и программирование")
                                                                              .filter(education_basis="Бюджет").filter(is_in_academ=False))

                        worksheet.merge_cells(f"G{entry_index+(len(qualifications_specialty) - 1)}:G{entry_index+(len(qualifications_specialty)*2 - 3)}")
                        worksheet.cell(row=entry_index+len(qualifications_specialty)-1, column=7).fill = PatternFill("solid", fgColor=Color(indexed=7))
                        worksheet.cell(row=entry_index+len(qualifications_specialty)-1, column=7).value = len(self.students.filter(group__qualification__name="Информационные системы и программирование")
                                                                                                              .filter(education_basis="Внебюджет").filter(is_in_academ=False))
                        
                        # Академ отпуск
                        worksheet.merge_cells(f"N{entry_index}:N{entry_index+(len(qualifications_specialty)-2)}")
                        worksheet.cell(row=entry_index, column=14).fill = PatternFill("solid", fgColor=Color(indexed=3))
                        worksheet.cell(row=entry_index, column=14).value = len(self.students.filter(group__qualification__name="Информационные системы и программирование")
                                                                               .filter(education_basis="Бюджет").filter(is_in_academ=True))

                        worksheet.merge_cells(f"N{entry_index+len(qualifications_specialty) - 1}:N{entry_index+(len(qualifications_specialty)*2 - 3)}")
                        worksheet.cell(row=entry_index+len(qualifications_specialty)-1, column=14).fill = PatternFill("solid", fgColor=Color(indexed=7))
                        worksheet.cell(row=entry_index+len(qualifications_specialty)-1, column=14).value = len(self.students.filter(group__qualification__name="Информационные системы и программирование")
                                                                                                               .filter(education_basis="Внебюджет").filter(is_in_academ=True))

                        worksheet.merge_cells(f"S{entry_index}:S{entry_index+(len(qualifications_specialty)*2 - 3)}")
                        worksheet.cell(row=entry_index, column=19).value = "Итог без учета 1-го курса специальности 09.02.07"

                        isip_done = True
                    
                    # В случае если нам попадается эта квалификация (это 1-ый курс исипа),
                    # ничего не делаем, т.к. до этого мы уже с ними разобрались
                    if qualification.name == "Информационные системы и программирование":
                        continue
                    
                    worksheet.cell(row=entry_index,column=1).value = entry_count
                    worksheet.cell(row=entry_index,column=2).value = specialty.code
                    worksheet.cell(row=entry_index,column=3).value = specialty.name
                    worksheet.cell(row=entry_index,column=4).value = qualification.name
                    worksheet.cell(row=entry_index,column=5).value = "Очная"

                    students_qualification = self.students.filter(group__qualification__name=qualification.name)
                    # Здесь у меня два варианта развитий в зависимости от того присутствуют ли на квалификации
                    # бюджетники или нет. Это влияет на объединение строк и последующую логику их заполнения
                    if len(students_qualification.filter(education_basis="Бюджет")) > 0:
                        worksheet.merge_cells(f"A{entry_index}:A{entry_index+1}")
                        worksheet.merge_cells(f"B{entry_index}:B{entry_index+1}")
                        worksheet.merge_cells(f"C{entry_index}:C{entry_index+1}")
                        worksheet.merge_cells(f"D{entry_index}:D{entry_index+1}")
                        worksheet.merge_cells(f"E{entry_index}:E{entry_index+1}")
                        
                        worksheet.cell(row=entry_index, column=6).value = "Бюджет"
                        worksheet.cell(row=entry_index+1, column=6).value = "Договор"

                        # Суммарное количество всех студентов на квалификации (Бюджет и договор)
                        worksheet.cell(row=entry_index, column=18).value = len(students_qualification.filter(education_basis="Бюджет"))
                        worksheet.cell(row=entry_index+1, column=18).value = len(students_qualification.filter(education_basis="Внебюджет"))

                        # 9 классники
                        for course in range(1, 5):
                            if not(course == 1 and specialty.name == "Информационные системы и программирование"): 
                                worksheet.cell(row=entry_index, column=6+course).value = len(students_qualification.filter(group__current_course=course).filter(education_basis="Бюджет")
                                                                                             .filter(education_base="Основное общее").filter(is_in_academ=False))
                                worksheet.cell(row=entry_index+1, column=6+course).value = len(students_qualification.filter(group__current_course=course).filter(education_basis="Внебюджет")
                                                                                               .filter(education_base="Основное общее").filter(is_in_academ=False))
                                # Академ отпуска (и для 9 и для 11)
                                worksheet.cell(row=entry_index, column=13+course).value = len(students_qualification.filter(group__current_course=course).filter(education_basis="Бюджет")
                                                                                              .filter(is_in_academ=True))
                                worksheet.cell(row=entry_index+1, column=13+course).value = len(students_qualification.filter(group__current_course=course).filter(education_basis="Внебюджет")
                                                                                              .filter(is_in_academ=True))
                        # 11 классники
                        for course in range(1, 4):
                             worksheet.cell(row=entry_index, column=10+course).value = len(students_qualification.filter(group__current_course=course).filter(education_basis="Бюджет")
                                                                                             .filter(education_base="Среднее общее").filter(is_in_academ=False))
                             worksheet.cell(row=entry_index+1, column=10+course).value = len(students_qualification.filter(group__current_course=course).filter(education_basis="Внебюджет")
                                                                                             .filter(education_base="Среднее общее").filter(is_in_academ=False))
                        entry_index += 2

                    else:
                        worksheet.cell(row=entry_index, column=6).value = "Договор"

                        # Суммарное количество всех студентов на квалификации (Договор)
                        worksheet.cell(row=entry_index, column=18).value = len(students_qualification.filter(education_basis="Внебюджет"))
                        
                        # 9 классники
                        for course in range(1, 5):
                            worksheet.cell(row=entry_index, column=6+course).value = len(students_qualification.filter(group__current_course=course).filter(education_base="Основное общее")
                                                                                         .filter(is_in_academ=False))
                            # Академ отпуска (для 9 и 11)
                            worksheet.cell(row=entry_index, column=13+course).value = len(students_qualification.filter(group__current_course=course).filter(is_in_academ=True))
                        # 11 классники
                        for course in range(1, 4):
                            worksheet.cell(row=entry_index, column=10+course).value = len(students_qualification.filter(group__current_course=course).filter(education_base="Среднее общее")
                                                                                          .filter(is_in_academ=False))
                        entry_index += 1
                    
                    
                    entry_count += 1
            
            # Итог под каждый курс
            for column_num in range(7, 19):
                worksheet.cell(row=entry_index, column=column_num).fill = PatternFill("solid", fgColor=Color(indexed=5))

            worksheet.cell(row=entry_index, column=7).value = len(self.students.filter(education_base="Основное общее").filter(group__current_course=1)
                                                                   .filter(is_in_academ=False))
            worksheet.cell(row=entry_index, column=8).value = len(self.students.filter(education_base="Основное общее").filter(group__current_course=2)
                                                                   .filter(is_in_academ=False))
            worksheet.cell(row=entry_index, column=9).value = len(self.students.filter(education_base="Основное общее").filter(group__current_course=3)
                                                                   .filter(is_in_academ=False))
            worksheet.cell(row=entry_index, column=10).value = len(self.students.filter(education_base="Основное общее").filter(group__current_course=4)
                                                                   .filter(is_in_academ=False))
            worksheet.cell(row=entry_index, column=11).value = len(self.students.filter(education_base="Среднее общее").filter(group__current_course=1)
                                                                   .filter(is_in_academ=False))
            worksheet.cell(row=entry_index, column=12).value = len(self.students.filter(education_base="Среднее общее").filter(group__current_course=2)
                                                                   .filter(is_in_academ=False))
            worksheet.cell(row=entry_index, column=13).value = len(self.students.filter(education_base="Среднее общее").filter(group__current_course=3)
                                                                   .filter(is_in_academ=False))
            worksheet.cell(row=entry_index, column=14).value = len(self.students.filter(group__current_course=1).filter(is_in_academ=True))
            worksheet.cell(row=entry_index, column=15).value = len(self.students.filter(group__current_course=2).filter(is_in_academ=True))
            worksheet.cell(row=entry_index, column=16).value = len(self.students.filter(group__current_course=3).filter(is_in_academ=True))
            worksheet.cell(row=entry_index, column=17).value = len(self.students.filter(group__current_course=4).filter(is_in_academ=True))

            # Итог со всеми студентами
            worksheet.cell(row=entry_index, column=18).value = len(self.students)
            worksheet.cell(row=entry_index+2, column=17).value = "Итого:"
            worksheet.cell(row=entry_index+2, column=18).value = len(self.students)
            
            # Итог с ИСИП
            worksheet.cell(row=entry_index+5, column=2).fill = PatternFill("solid", fgColor=Color(indexed=3))
            worksheet.cell(row=entry_index+5, column=2).value = len(self.students.filter(group__qualification__name="Информационные системы и программирование")
                                                                  .filter(education_basis="Бюджет").filter(is_in_academ=False))
            worksheet.cell(row=entry_index+6, column=2).fill = PatternFill("solid", fgColor=Color(indexed=7))
            worksheet.cell(row=entry_index+6, column=2).value = len(self.students.filter(group__qualification__name="Информационные системы и программирование")
                                                                  .filter(education_basis="Внебюджет").filter(is_in_academ=False))
            worksheet.cell(row=entry_index+5, column=3).value = "- бюджет"
            worksheet.cell(row=entry_index+6, column=3).value = "- договор"
        workbook.save(path)

class VacationTableGenerator:
    pass

class MovementTableGenerator:
    pass

# def tableStudentsParse(path):
#     ext = os.path.splitext(path)[1].lower()
#     data = []
#     if ext == ".xlsx":
#         workbook = load_workbook(filename=path, data_only=True)
#         worksheet = workbook.active
#         if worksheet is not None:
#             for row in worksheet.iter_rows(values_only=True):
#                 data.append(list(row))
#     elif ext == ".xls":
#         import xlrd
#         workbook = xlrd.open_workbook(path)
#         worksheet = workbook.sheet_by_index(0)
#         for row_index in range(worksheet.nrows):
#             data.append(worksheet.row_values(row_index))
#     else:
#         ValueError("Неподдерживаемый формат файла")
#     
#     students = []
#     for student_row in data:
#        student = Student(full_name=student_row[1], )

# if __name__ == "__main__":
    # students = Student.objects.all()
    # students_course = Student.objects.filter(group__current_course="1")
    # specialties = Specialty.objects.all()
    # qualifications = Qualification.objects.all()
    # groups = GroupStudents.objects.all()

    # gtg = GroupTableGenerator(groups=groups)
    # ctg = CourseTableGenerator(students=students_course)
    # stg = StatisticsTableGenerator(specialties=specialties, qualifications=qualifications, students=students)

    # gtg.generate_document("test_groups.xlsx")
    # ctg.generate_document("test_course.xlsx")
    # stg.generate_document("test_statistics.xlsx")
