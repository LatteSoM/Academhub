from django.contrib import admin
from Curriculum.models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Discipline)
admin.site.register(MiddleCertification)
admin.site.register(ProfessionalModule)
admin.site.register(Practice)
admin.site.register(TermPaper)
admin.site.register(Specialty)
admin.site.register(Qualification)
admin.site.register(CurriculumItem)
admin.site.register(Curriculum)
admin.site.register(RecordBookTemplate)
admin.site.register(GroupStudents)
admin.site.register(Student)
admin.site.register(StudentRecordBook)
admin.site.register(GradebookStudents)
admin.site.register(Gradebook)
admin.site.register(CalendarGraphicOfLearningProcess)
admin.site.register(ContingentMovement)
admin.site.register(PermissionProxy)
admin.site.register(GroupProxy)
