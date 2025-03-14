from django.contrib import admin
from .models import StudyPlan, Category, StudyCycle, Module, Disipline, ClockCell, WhitelistWord


class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'qualification', 'admission_year', 'create_date')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'identificator', 'cycles', 'study_plan')

class StudyCycleAdmin(admin.ModelAdmin):
    list_display = ('id', 'identificator', 'cycles', 'category')

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'studey_cycle')

class DisiplineAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'index', 'module')

class ClockCellAdmin(admin.ModelAdmin):
    list_display = ('id', 'code_of_type_work', 'code_of_type_hours', 'course', 'semestr', 'count_of_clocks', 'plan_string', 'module_plan_string')

class WhitelistWordAdmin(admin.ModelAdmin):
    list_display = ('word',)

admin.site.register(StudyPlan, StudyPlanAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(StudyCycle, StudyCycleAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Disipline, DisiplineAdmin)
admin.site.register(ClockCell, ClockCellAdmin)
admin.site.register(WhitelistWord, WhitelistWordAdmin)
