from django.db import models

# New models for Curriculum app - REFACTORED

class StudyPlan(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    qualification = models.CharField(max_length=255, null=True)
    admission_year = models.CharField(max_length=255, null=True)
    create_date = models.DateField(null=True)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"REFACTORED StudyPlan: {self.qualification} ({self.admission_year})"

class Category(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    identificator = models.CharField(max_length=255, null=True)
    cycles = models.CharField(max_length=255, null=True)
    study_plan = models.ForeignKey(StudyPlan, related_name='cycles', on_delete=models.CASCADE)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"REFACTORED Category: {self.cycles} ({self.study_plan.id})"

class StudyCycle(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    identificator = models.CharField(max_length=255, null=True)
    cycles = models.CharField(max_length=255, null=True)
    category = models.ForeignKey(Category, related_name='child_cycles', on_delete=models.CASCADE)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"REFACTORED StudyCycle: {self.cycles} ({self.category.id})"

class Module(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255, null=True)
    studey_cycle = models.ForeignKey(StudyCycle, related_name='plan_strings', on_delete=models.CASCADE)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"REFACTORED Module: {self.name} ({self.studey_cycle.id})"

class Disipline(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255, null=True)
    index = models.CharField(max_length=255, null=True)  # Добавляем поле для индекса
    module = models.ForeignKey(Module, related_name='child_plan_strings', on_delete=models.CASCADE)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"REFACTORED Discipline: {self.name} ({self.module.id})"

class ClockCell(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    code_of_type_work = models.CharField(max_length=255, null=True)
    code_of_type_hours = models.CharField(max_length=255, null=True)
    course = models.IntegerField(null=True)
    semestr = models.IntegerField(null=True)
    count_of_clocks = models.IntegerField(null=True)
    plan_string = models.ForeignKey(Disipline, related_name='clock_cells', on_delete=models.CASCADE, null=True)
    module_plan_string = models.ForeignKey(Module, related_name='clock_cells', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"REFACTORED ClockCell: Course {self.course}, Semester {self.semestr}, Clocks: {self.count_of_clocks}"

class WhitelistWord(models.Model):
    word = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"REFACTORED WhitelistWord: {self.word}"
