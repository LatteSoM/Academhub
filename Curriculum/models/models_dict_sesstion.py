class QualificationDict:
    """Программист, Веб-дизайнер и т.д."""
    def __init__(self, short_name, name, specialty):
        self.short_name = short_name
        self.name = name
        self.specialty = specialty

    def to_dict(self):
        return {
            "short_name": self.short_name,
            "name": self.name,
            "specialty": self.specialty,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            short_name=data.get("short_name"),
            name=data.get("name"),
            specialty=data.get("specialty"),
        )


class SpecialtyDict:
    """Например: 09.02.07"""
    def __init__(self, code, name):
        self.code = code
        self.name = name

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            code=data.get("code"),
            name=data.get("name"),
        )


class CurriculumDict:
    """Учебный план"""
    def __init__(self, qualification_name=None, warnings=False, warning_description=None, qualification=None, admission_year=None):
        self.qualification_name = qualification_name
        self.warnings = warnings
        self.warning_description = warning_description if warning_description else {}
        self.qualification = qualification if qualification else {}
        self.admission_year = admission_year

    def to_dict(self):
        return {
            "qualification_name": self.qualification_name,
            "warnings": self.warnings,
            "warning_description": self.warning_description,
            "qualification": self.qualification,
            "admission_year": self.admission_year,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            qualification_name=data.get("qualification_name"),
            warnings=data.get("warnings", False),
            warning_description=data.get("warning_description", {}),
            qualification=data.get("qualification", {}),
            admission_year=data.get("admission_year"),
        )


class CategoryDict:
    """Категория"""
    def __init__(self, identificator, cycles, curriculum=None, warnings=False, warning_description=None):
        self.identificator = identificator
        self.cycles = cycles
        self.curriculum = curriculum if curriculum else {}
        self.warnings = warnings
        self.warning_description = warning_description if warning_description else {}

    def to_dict(self):
        return {
            "identificator": self.identificator,
            "cycles": self.cycles,
            "curriculum": self.curriculum,
            "warnings": self.warnings,
            "warning_description": self.warning_description,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            identificator=data.get("identificator"),
            cycles=data.get("cycles"),
            curriculum=data.get("curriculum", {}),
            warnings=data.get("warnings", False),
            warning_description=data.get("warning_description", {}),
        )


class StudyCycleDict:
    """Образовательный цикл"""
    def __init__(self, identificator, cycles, categories=None, warnings=False, warning_description=None):
        self.identificator = identificator
        self.cycles = cycles
        self.categories = categories if categories else {}
        self.warnings = warnings
        self.warning_description = warning_description if warning_description else {}

    def to_dict(self):
        return {
            "identificator": self.identificator,
            "cycles": self.cycles,
            "categories": self.categories,
            "warnings": self.warnings,
            "warning_description": self.warning_description,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            identificator=data.get("identificator"),
            cycles=data.get("cycles"),
            categories=data.get("categories", {}),
            warnings=data.get("warnings", False),
            warning_description=data.get("warning_description", {}),
        )


class ModuleDict:
    """Модуль"""
    def __init__(self, module_name, code_of_discipline, code_of_cycle_block, study_cycles=None, warnings=False, warning_description=None):
        self.module_name = module_name
        self.code_of_discipline = code_of_discipline
        self.code_of_cycle_block = code_of_cycle_block
        self.study_cycles = study_cycles if study_cycles else {}
        self.warnings = warnings
        self.warning_description = warning_description if warning_description else {}

    def to_dict(self):
        return {
            "module_name": self.module_name,
            "code_of_discipline": self.code_of_discipline,
            "code_of_cycle_block": self.code_of_cycle_block,
            "study_cycles": self.study_cycles,
            "warnings": self.warnings,
            "warning_description": self.warning_description,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            module_name=data.get("module_name"),
            code_of_discipline=data.get("code_of_discipline"),
            code_of_cycle_block=data.get("code_of_cycle_block"),
            study_cycles=data.get("study_cycles", {}),
            warnings=data.get("warnings", False),
            warning_description=data.get("warning_description", {}),
        )


class DisciplineDict:
    """Дисциплина"""
    def __init__(self, code, discipline_name, cycle_relation, specialty=None, module=None, curriculums=None, warnings=False, warning_description=None):
        self.code = code
        self.discipline_name = discipline_name
        self.specialty = specialty if specialty else {}
        self.module = module if module else {}

        self.cycle_relation = cycle_relation

        self.warnings = warnings
        self.warning_description = warning_description if warning_description else {}

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.discipline_name,
            "specialty": self.specialty,
            "module": self.module,
            "cycle_relation": self.cycle_relation,
            "warnings": self.warnings,
            "warning_description": self.warning_description,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            code=data.get("code"),
            discipline_name=data.get("discipline_name"),
            specialty=data.get("specialty", {}),
            module=data.get("module", {}),
            cycle_relation=data.get("cycle_relation"),
            warnings=data.get("warnings", False),
            warning_description=data.get("warning_description", {}),
        )

class ClockCellDict:
    """Ячейка часов"""
    def __init__(self, code_of_type_work, code_of_type_hours, course, term, count_of_clocks, curriculum,
        warnings=False, warning_description=None, module=None, discipline=None):

        self.code_of_type_work = code_of_type_work
        self.code_of_type_hours = code_of_type_hours
        self.course = course
        self.term = term
        self.module = module if module else None
        self.discipline = discipline if discipline else None
        self.curriculum = curriculum
        self.count_of_clocks = count_of_clocks
        self.warnings = warnings
        self.warning_description = warning_description if warning_description else {}

    def to_dict(self):
        return {
            "code_of_type_work": self.code_of_type_work,
            "code_of_type_hours": self.code_of_type_hours,
            "course": self.course,
            "term": self.term,
            "count_of_clocks": self.count_of_clocks,
            "module": self.module,
            "curriculum": self.curriculum,
            "discipline": self.discipline,
            "warnings": self.warnings,
            "warning_description": self.warning_description,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            code_of_type_work=data.get("code_of_type_work"),
            code_of_type_hours=data.get("code_of_type_hours"),
            course=data.get("course"),
            term=data.get("term"),
            module=data.get("module"),
            curriculum=data.get("curriculum"),
            discipline=data.get("discipline"),
            count_of_clocks=data.get("count_of_clocks"),
            warnings=data.get("warnings", False),
            warning_description=data.get("warning_description", {}),
        )