from django.contrib import admin


from django.contrib.auth.models import Group, Permission
from Academhub.models import CustomUser, GradebookStudents, Discipline, Specialty, Qualification, GroupStudents, \
    Student, Gradebook, Curriculum, TermPaper, Practice, ProfessionalModule, MiddleCertification, RecordBookTemplate, \
    StudentRecordBook, CalendarGraphicOfLearningProcess, \
    Student, Gradebook, Curriculum, TermPaper, Practice, ProfessionalModule, MiddleCertification, RecordBookTemplate, \
    StudentRecordBook, CurriculumItem, PracticeDate

admin.site.register(CustomUser)
admin.site.register(GroupStudents)
admin.site.register(Permission)
admin.site.register(Discipline)
admin.site.register(Specialty)
admin.site.register(Qualification)
admin.site.register(Student)
admin.site.register(Gradebook)
admin.site.register(GradebookStudents)
admin.site.register(Curriculum)
admin.site.register(TermPaper)
admin.site.register(Practice)
admin.site.register(ProfessionalModule)
admin.site.register(MiddleCertification)
admin.site.register(RecordBookTemplate)
admin.site.register(StudentRecordBook)
admin.site.register(CalendarGraphicOfLearningProcess)
admin.site.register(CurriculumItem)
admin.site.register(PracticeDate)