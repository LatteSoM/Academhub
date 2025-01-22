"""
URL configuration for Academhub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from .views import *
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', HomeView.as_view(), name='home'),
    path('auth/', auth, name='auth'),

    path('contingent/', include('Сontingent.urls')),
]

# from django.db import models

# class QualificationDTO(models.Model):
#     union_name = models.CharField(
#         max_length=255, 
#         verbose_name='Союз Название'
#     )
#     name = models.CharField(
#         max_length=255, 
#         verbose_name='Наименование'
#     )

#     def __str__(self):
#         return self.name

# class SpecializationDTO(models.Model):
#     code = models.CharField(
#         max_length=50, 
#         verbose_name='код'
#     )
#     name = models.CharField(
#         max_length=255, 
#         verbose_name='Наименование'
#     )

#     def __str__(self):
#         return self.name

# class GroupDTO(models.Model):
#     qualification = models.ForeignKey(
#         QualificationDTO, 
#         on_delete=models.CASCADE, 
#         verbose_name='Квалификация'
#     )
#     specialization = models.ForeignKey(
#         SpecializationDTO, 
#         on_delete=models.CASCADE, 
#         verbose_name='специальность (FK)'
#     )

#     def __str__(self):
#         return f"Группа {self.id} - {self.qualification.name} ({self.specialization.name})"

# class StudentDTO(models.Model):
#     full_name = models.CharField(
#         max_length=255, 
#         verbose_name='ФИО'
#     )
#     phone = models.CharField(
#         max_length=20, 
#         verbose_name='телефон'
#     )
#     birth_date = models.DateField(
#         verbose_name='Дата рождения'
#     )
#     course = models.IntegerField(
#         verbose_name='курс'
#     )
#     group = models.ForeignKey(
#         GroupDTO, 
#         on_delete=models.CASCADE, 
#         verbose_name='группа(FK)'
#     )
#     enrollment_order = models.CharField(
#         max_length=255, 
#         verbose_name='приказ о зачислении'
#     )
#     transfer_to_second_course_order = models.CharField(
#         max_length=255, 
#         blank=True, 
#         null=True, 
#         verbose_name='приказ о переводе на 2 курс'
#     )
#     transfer_to_third_course_order = models.CharField(
#         max_length=255, 
#         blank=True, 
#         null=True, 
#         verbose_name='приказ о переводе на 3 курс'
#     )
#     transfer_to_fourth_course_order = models.CharField(
#         max_length=255, 
#         blank=True, 
#         null=True, 
#         verbose_name='приказ о переводе на 4 курс'
#     )
#     graduation_order = models.CharField(
#         max_length=255, 
#         blank=True, 
#         null=True, 
#         verbose_name='Отчислен в связи с окончанием обучения'
#     )
#     education_base = models.CharField(
#         max_length=255, 
#         verbose_name='база образования'
#     )
#     education_reason = models.CharField(
#         max_length=255, 
#         verbose_name='основа образования'
#     )
#     registration_address = models.CharField(
#         max_length=255, 
#         verbose_name='адрес прописка'
#     )
#     actual_address = models.CharField(
#         max_length=255, 
#         verbose_name='адрес фактический'
#     )
#     representative_name = models.CharField(
#         max_length=255, 
#         verbose_name='ФИО представителя'
#     )
#     representative_email = models.EmailField(
#         verbose_name='почта представителя'
#     )
#     notes = models.TextField(
#         blank=True, 
#         null=True, 
#         verbose_name='примечание'
#     )
#     previous_course = models.IntegerField(
#         blank=True, 
#         null=True, 
#         verbose_name='курс с которого ушел'
#     )

#     def __str__(self):
#         return self.full_name