# from django.db import models
# from Academhub.models import AcademHubModel
#
# class QualificationDTO(AcademHubModel):
#     union_name = models.CharField(
#         max_length=255,
#         verbose_name='Наименование (сокращение)'
#     )
#     name = models.CharField(
#         max_length=255,
#         verbose_name='Наименование'
#     )
#
#     def __str__(self):
#         return self.name
#
# class SpecializationDTO(AcademHubModel):
#     code = models.CharField(
#         max_length=50,
#         verbose_name='код'
#     )
#     name = models.CharField(
#         max_length=255,
#         verbose_name='Наименование'
#     )
#
#     def __str__(self):
#         return self.name
#
# class GroupDTO(AcademHubModel):
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
#     group_name = models.CharField(
#         verbose_name='Номер группы',
#         max_length=255,
#         null=True,
#     )
#
#     def __str__(self):
#         return f"{self.qualification.name} ({self.group_name})"
#
# class StudentDTO(AcademHubModel):
#     class Meta:
#         verbose_name = 'Студент'
#         verbose_name_plural = 'Студенты'
#
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
#         verbose_name='группа(FK)',
#         null=True,
#         blank=True
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
#
#     def __str__(self):
#         return self.full_name
#
#
# # # class User(AcademHubModel):
# # #     id = models.AutoField(primary_key=True)
# # #     login = models.CharField(max_length=150, unique=True, verbose_name="Логин")
# # #     password = models.CharField(max_length=128, verbose_name="Пароль")
# # #     full_name = models.CharField(max_length=255, verbose_name="ФИО")
# # #     is_teacher = models.BooleanField(default=False, verbose_name="Преподаватель")
# # #
# # #     class Meta:
# # #         verbose_name = "Пользователь"
# # #         verbose_name_plural = "Пользователи"
# # #
# # #     def __str__(self):
# # #         return self.full_name
# # #
# # # class GroupPermission(AcademHubModel):
# # #     id = models.AutoField(primary_key=True)
# # #     name = models.CharField(max_length=255, verbose_name="Право")
# # #
# # #     class Meta:
# # #         verbose_name = "Группа прав"
# # #         verbose_name_plural = "Группы прав"
# # #
# # #     def __str__(self):
# # #         return self.name
# # #
# # # class Permission(AcademHubModel):
# # #     id = models.AutoField(primary_key=True)
# # #     name = models.CharField(max_length=255, verbose_name="Право")
# # #     groups = models.ManyToManyField(GroupPermission, related_name="permissions", verbose_name="Группы прав")
# # #     users = models.ManyToManyField(User, related_name="permissions", verbose_name="Пользователи")
# # #
# # #     class Meta:
# # #         verbose_name = "Право"
# # #         verbose_name_plural = "Права"
# # #
# # #     def __str__(self):
# # #         return self.name
# # #
# # # class Discipline(AcademHubModel):
# # #     id = models.AutoField(primary_key=True)
# # #     code = models.CharField(max_length=50, unique=True, verbose_name="Код")
# # #     name = models.CharField(max_length=255, verbose_name="Наименование")
# # #     specialty = models.ForeignKey(
# # #         'Specialty', on_delete=models.CASCADE, related_name="disciplines", verbose_name="Специальность"
# # #     )
# # #
# # #     class Meta:
# # #         verbose_name = "Дисциплина"
# # #         verbose_name_plural = "Дисциплины"
# # #
# # #     def __str__(self):
# # #         return self.name
# # #
# # # class Specialty(AcademHubModel):
# # #     id = models.AutoField(primary_key=True)
# # #     code = models.CharField(max_length=50, unique=True, verbose_name="Код")
# # #     name = models.CharField(max_length=255, verbose_name="Наименование")
# # #
# # #     class Meta:
# # #         verbose_name = "Специальность"
# # #         verbose_name_plural = "Специальности"
# # #
# # #     def __str__(self):
# # #         return self.name
# # #
# # # class Qualification(AcademHubModel):
# # #     id = models.AutoField(primary_key=True)
# # #     short_name = models.CharField(max_length=50, verbose_name="Сокращенное название")
# # #     name = models.CharField(max_length=255, verbose_name="Наименование")
# # #     specialty = models.ForeignKey(
# # #         Specialty, on_delete=models.CASCADE, related_name="qualifications", verbose_name="Специальность"
# # #     )
# # #
# # #     class Meta:
# # #         verbose_name = "Квалификация"
# # #         verbose_name_plural = "Квалификации"
# # #
# # #     def __str__(self):
# # #         return self.name
# # #
# # # class Group(AcademHubModel):
# # #     id = models.AutoField(primary_key=True)
# # #     number = models.CharField(max_length=50, unique=True, verbose_name="Номер")
# # #     qualification = models.ForeignKey(
# # #         Qualification, on_delete=models.CASCADE, related_name="groups", verbose_name="Квалификация"
# # #     )
# # #
# # #     class Meta:
# # #         verbose_name = "Группа"
# # #         verbose_name_plural = "Группы"
# # #
# # #     def __str__(self):
# # #         return self.number
# # #
# # # class Student(AcademHubModel):
# # #     id = models.AutoField(primary_key=True)
# # #     full_name = models.CharField(max_length=255, verbose_name="ФИО")
# # #     phone = models.CharField(max_length=15, verbose_name="Телефон")
# # #     birth_date = models.DateField(verbose_name="Дата рождения")
# # #     course = models.IntegerField(verbose_name="Курс")
# # #     group = models.ForeignKey(
# # #         Group, on_delete=models.CASCADE, related_name="students", verbose_name="Группа"
# # #     )
# # #     admission_order = models.CharField(
# # #         max_length=255, verbose_name="Приказ о зачислении"
# # #     )
# # #     transfer_to_2nd_year_order = models.CharField(
# # #         max_length=255, verbose_name="Приказ о переводе на 2 курс", blank=True, null=True
# # #     )
# # #     transfer_to_3rd_year_order = models.CharField(
# # #         max_length=255, verbose_name="Приказ о переводе на 3 курс", blank=True, null=True
# # #     )
# # #     transfer_to_4th_year_order = models.CharField(
# # #         max_length=255, verbose_name="Приказ о переводе на 4 курс", blank=True, null=True
# # #     )
# # #     expelled_due_to_graduation = models.BooleanField(
# # #         default=False, verbose_name="Отчислен в связи с окончанием обучения"
# # #     )
# # #     education_base = models.CharField(
# # #         max_length=255, verbose_name="База образования"
# # #     )
# # #     education_basis = models.CharField(
# # #         max_length=255, verbose_name="Основа образования"
# # #     )
# # #     registration_address = models.TextField(
# # #         verbose_name="Адрес прописки"
# # #     )
# # #     actual_address = models.TextField(
# # #         verbose_name="Адрес фактический"
# # #     )
# # #     representative_full_name = models.CharField(
# # #         max_length=255, verbose_name="ФИО представителя"
# # #     )
# # #     representative_email = models.EmailField(
# # #         verbose_name="Почта представителя"
# # #     )
# # #     note = models.TextField(blank=True, null=True, verbose_name="Примечание")
# # #     left_course = models.IntegerField(
# # #         blank=True, null=True, verbose_name="Курс, с которого ушел"
# # #     )
# # #
# # #     class Meta:
# # #         verbose_name = "Студент"
# # #         verbose_name_plural = "Студенты"
# # #
# # #     def __str__(self):
# # #         return self.full_name
# # #
# # # class Gradebook(AcademHubModel):
# # #     id = models.AutoField(primary_key=True)
# # #     teacher = models.ForeignKey(
# # #         User, on_delete=models.CASCADE, related_name="gradebooks", verbose_name="Преподаватель"
# # #     )
# # #     number = models.CharField(max_length=50, verbose_name="Номер")
# # #     name = models.CharField(max_length=255, verbose_name="Наименование")
# # #     group = models.ForeignKey(
# # #         Group, on_delete=models.CASCADE, related_name="gradebooks", verbose_name="Группа"
# # #     )
# # #     discipline = models.ForeignKey(
# # #         Discipline, on_delete=models.CASCADE, related_name="gradebooks", verbose_name="Дисциплина"
# # #     )
# # #     status = models.CharField(max_length=50, verbose_name="Статус")
# # #
# # #     class Meta:
# # #         verbose_name = "Ведомость"
# # #         verbose_name_plural = "Ведомости"
# # #
# # #     def __str__(self):
# # #         return self.name
