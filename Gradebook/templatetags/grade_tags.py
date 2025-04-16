from datetime import timezone

from django import template
from Academhub.models import GradebookStudents
import logging

register = template.Library()
logger = logging.getLogger(__name__)


@register.filter
def get_grade(student, discipline):
    """
    Возвращает самую последнюю оценку студента по дисциплине на основе даты закрытия ведомости.
    Учитывает только закрытые ведомости (status='Закрыта' и date_of_closing в прошлом).

    Args:
        student: Объект модели Student.
        discipline: Объект модели Discipline.

    Returns:
        Объект GradebookStudents с последней оценкой или None, если оценок нет.
    """
    # Получаем самую последнюю закрытую ведомость студента по дисциплине
    latest_grade = student.gradebookstudents_set.filter(
        gradebook__discipline=discipline,
        gradebook__status='Закрыта'
    ).select_related('gradebook').order_by('-gradebook__date_of_closing').first()

    if latest_grade:
        logger.debug(
            f"Grade for student {student.full_name}, discipline {discipline.name}: "
            f"{latest_grade.grade} (type: {latest_grade.gradebook.type_of_grade_book}, "
            f"closed: {latest_grade.gradebook.date_of_closing})"
        )
        return latest_grade

    # Если ничего не найдено
    logger.debug(f"Grade for student {student.full_name}, discipline {discipline.name}: None")
    return None

@register.filter
def get_grade_for_semester(grade, semester):
    if grade and grade.gradebook.semester_number == semester:
        return grade
    return None

@register.filter
def filter_bad_grades(grades):
    return [g for g in grades if g and g.grade in ['2', 'Неявка']]

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

@register.simple_tag
def get_semesters_order(disciplines):
    return sorted({d[1] for d in disciplines})

@register.filter
def get_all_grades(student, disciplines_with_semesters):
    """Возвращает все оценки студента для списка (дисциплина, семестр, часы, имя)."""
    grades = []
    for discipline, semester, hours, display_name in disciplines_with_semesters:  # Распаковываем четыре значения
        grade = GradebookStudents.objects.filter(
            student=student,
            gradebook__discipline=discipline,
            gradebook__semester_number=semester
        ).order_by('-gradebook__date_of_closing').first()
        grades.append(grade)
        logger.debug(f"Grade for {student.full_name}, {discipline.name}, semester {semester}: {grade.grade if grade else None}")
    return grades

@register.filter
def filter_valid_grades(grades):
    """Возвращает объект с количеством '4' и общим числом оценок."""
    valid_grades = [g for g in grades if g and g.grade not in ['2', 'Неявка']]
    return type('GradesSummary', (), {
        'count_4': len([g for g in valid_grades if g.grade == '4']),
        'total': len(valid_grades)
    })

@register.filter
def get_grade_for_discipline(student, discipline_semester):
    discipline, semester = discipline_semester
    grade_objs = student.gradebookstudents_set.filter(
        gradebook__discipline=discipline
    ).order_by('-gradebook__date_of_closing')
    return grade_objs.first()

@register.filter
def calculate_diploma_type(all_grades):
    bad_grades = [g for g in all_grades if str(g.grade).lower() in ['2', 'неявка', 'н/я', 'неудовлетворительно']]
    valid_grades = [g for g in all_grades if str(g.grade).lower() not in ['2', 'неявка', 'н/я', 'неудовлетворительно']]
    count_4 = len([g for g in valid_grades if g.grade == '4'])
    total_grades = len(valid_grades)
    return "Синий" if bad_grades or (total_grades and count_4 < total_grades * 0.25) else "Красный"