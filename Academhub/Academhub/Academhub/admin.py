from django.contrib import admin

from django.contrib.auth.models import Permission

from Academhub.models import CustomUser, GradebookStudents, Discipline, Specialty, Qualification, GroupStudents, \
    Student, Gradebook, Curriculum, TermPaper, Practice, ProfessionalModule, MiddleCertification, RecordBookTemplate, \
    StudentRecordBook, CalendarGraphicOfLearningProcess, \
    Student, Gradebook, Curriculum, TermPaper, Practice, ProfessionalModule, MiddleCertification, RecordBookTemplate, \
    StudentRecordBook, CurriculumItem, PracticeDate
from Academhub.models.models import ProgramSettings

admin.site.register(Student)
admin.site.register(Practice)
admin.site.register(Specialty)
admin.site.register(Gradebook)
admin.site.register(TermPaper)
admin.site.register(CustomUser)
admin.site.register(Permission)
admin.site.register(Discipline)
admin.site.register(Curriculum)
admin.site.register(PracticeDate)
# admin.site.register(ProgramSettings)
admin.site.register(GroupStudents)
admin.site.register(Qualification)
admin.site.register(CurriculumItem)
admin.site.register(GradebookStudents)
admin.site.register(StudentRecordBook)
admin.site.register(ProfessionalModule)
admin.site.register(RecordBookTemplate)
admin.site.register(MiddleCertification)
admin.site.register(CalendarGraphicOfLearningProcess)
