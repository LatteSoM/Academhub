from django.contrib import admin


from django.contrib.auth.models import Group, Permission
from Academhub.models import CustomUser, Discipline, Specialty, Qualification, GroupStudents, Student, Gradebook

admin.site.register(CustomUser)
admin.site.register(GroupStudents)
admin.site.register(Permission)
admin.site.register(Discipline)
admin.site.register(Specialty)
admin.site.register(Qualification)
admin.site.register(Student)
admin.site.register(Gradebook)