from typing import List

class CourseAndTermView:
    def __init__(self, course, term):
        self.course = course
        self.term = term

class DisciplineView:
    """
    Нужен для удобства работы с данными по дисциплине, семестрам и курсам во вьюшках
    """
    def __init__(self, id, code, name, when_going: List[CourseAndTermView] = []):
        self.id = id
        self.code = code
        self.name = name
        self.when_going = when_going
        