from django.db import models
from .models import AcademHubModel, Student
from .utils import UnifiedPermissionQyerySet
from django.contrib.auth.models import Permission, Group, PermissionManager

__all__ = (
    'GroupProxy',
    'AcademStudent',
    'CurrentStudent',
    'PermissionProxy',
    'ExpulsionStudent',
)

class UnifiedPermissionsManager(PermissionManager):
    '''
        Расширение менеджера модели Permisision
    '''

    def get_queryset(self):
        '''
            Добавление новых функция для работы с Queryset Permission
        '''
        return UnifiedPermissionQyerySet(self.model, using=self._db)

class PermissionProxy(AcademHubModel, Permission):
    '''
        Расширение для модели Permissions. Поддерживает навигацию
    '''

    objects = UnifiedPermissionsManager()

    class Meta:
        proxy = True
        ordering = ['pk']
        verbose_name = 'Право'
        verbose_name_plural = 'Права'

class GroupProxy(AcademHubModel, Group):
    '''
        Расширение для модели Group. Поддерживает навигацию
    '''

    class Meta:
        proxy = True
        verbose_name = 'Группа прав'
        verbose_name_plural = 'Группы прав'

class CurrentStudentManager(models.Manager):
    '''
        Менеджер для фильтрации не отчисленных и не находящихся в академическом отпуске студентов
    '''

    def get_queryset(self):
        return super().get_queryset().filter(is_in_academ=False, is_expelled=False)

class CurrentStudent(Student):

    objects = CurrentStudentManager()

    class Meta:
        proxy = True
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        

class AcademStudentManager(models.Manager):
    '''
        Менеджер для фильтрации студентов находящихся только в академическом отпуске
    '''
    def get_queryset(self):
        return super().get_queryset().filter(is_in_academ=True)

class AcademStudent(Student):
    '''
        Расширение для модели Student для получения всех студентов только в академ отпуске
    '''

    objects = AcademStudentManager()

    class Meta:
        proxy = True
        verbose_name = 'Студент в академическом отпуске'
        verbose_name_plural = 'Студенты в академичкском отпуске'
        permissions = [
            ('export_AcademStudent', 'Export AcademStudent')
        ]

class ExpulsionStudentManager(models.Manager):
    '''
        Менеджер для фильтрации отчисленных студентов
    '''
        
    def get_queryset(self):
        return super().get_queryset().filter(is_expelled=True)

class ExpulsionStudent(Student):
    '''
        Расширение для модели Stydent для получения всех отчисленных студентов
    '''

    objects = ExpulsionStudentManager()

    class Meta:
        proxy = True
        verbose_name = 'Отчисленные студент'
        verbose_name_plural = 'Отчисленные студенты'
