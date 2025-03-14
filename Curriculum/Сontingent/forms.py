from django import forms

# from Curriculum.models import Discipline, Student, GroupStudents, Qualification, Specialty, ContingentMovement

# TODO: Update forms to use new models.

# class DisciplineForm(forms.ModelForm):
#     """
#     Форма для дисциплины
#     """
#
#     class Meta:
#         model = Discipline
#         fields = '__all__'
#
#
# class StudentForm(forms.ModelForm):
#     """
#     Форма для студента
#     """
#
#     class Meta:
#         model = Student
#         fields = '__all__'
#
#
# class GroupForm(forms.ModelForm):
#     """
#     Форма для группы
#     """
#
#     class Meta:
#         model = GroupStudents
#         fields = '__all__'
#
#
# class QualificationForm(forms.ModelForm):
#     """
#     Форма для квалификации
#     """
#
#     class Meta:
#         model = Qualification
#         fields = '__all__'
#
#
# class SpecialtyForm(forms.ModelForm):
#     """
#     Форма для специальности
#     """
#
#     class Meta:
#         model = Specialty
#         fields = '__all__'
#
#
# class AcademLeaveForm(forms.ModelForm):
#     """
#     Форма для академического отпуска
#     """
#
#     class Meta:
#         model = ContingentMovement
#         fields = ['student', 'order_number', 'order_date', 'movement_type']
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.movement_type = 'academ_leave'
#         if commit:
#             instance.save()
#         return instance
#
#
# class AcademReturnForm(forms.ModelForm):
#     """
#     Форма для возвращения из академического отпуска
#     """
#
#     class Meta:
#         model = ContingentMovement
#         fields = ['student', 'order_number', 'order_date', 'movement_type']
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.movement_type = 'academ_return'
#         if commit:
#             instance.save()
#         return instance
#
#
# class ExpellStudentForm(forms.ModelForm):
#     """
#     Форма для отчисления студента
#     """
#
#     class Meta:
#         model = ContingentMovement
#         fields = ['student', 'order_number', 'order_date', 'movement_type']
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.movement_type = 'expelled'
#         if commit:
#             instance.save()
#         return instance
#
#
# class RecoverStudentForm(forms.ModelForm):
#     """
#     Форма для восстановления студента
#     """
#
#     class Meta:
#         model = ContingentMovement
#         fields = ['student', 'order_number', 'order_date', 'movement_type']
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.movement_type = 'recovered'
#         if commit:
#             instance.save()
#         return instance
#
#
# class StudentImportForm(forms.Form):
#     """
#     Форма для импорта студентов
#     """
#     file = forms.FileField()