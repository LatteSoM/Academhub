from django.contrib import admin

from Academhub.models import User, GroupPermission, Permission, Discipline, Specialty, Qualification, Group, Student, \
    Gradebook

admin.site.register(User)
admin.site.register(GroupPermission)
admin.site.register(Permission)
admin.site.register(Discipline)
admin.site.register(Specialty)
admin.site.register(Qualification)
admin.site.register(Group)
admin.site.register(Student)
admin.site.register(Gradebook)