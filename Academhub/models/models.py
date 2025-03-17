import uuid
from ..validators import *
from django.db import models
from django.urls import reverse
from django.db.models import ManyToManyField
from django.utils import timezone
from .mixin import UrlGenerateMixin
from .utils import UnifiedPermissionQyerySet
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Permission, Group, PermissionsMixin, PermissionManager


__all__ = (
    'Student',
    'Practice',
    'Gradebook',
    'Specialty',
    'TermPaper',
    'CustomUser',
    'GroupProxy',
    'PracticeDate',
    'GroupStudents',
    'Qualification',
    'AcademHubModel',
    'CurriculumItem',
    'PermissionProxy',
    'StudentRecordBook',
    'GradebookStudents',
    'ProfessionalModule',
    'RecordBookTemplate',
    'ContingentMovement',
    'MiddleCertification',
    'MiddleCertification',
    'StudentRecordBook',
    'RecordBookTemplate',
    'CalendarGraphicOfLearningProcess',

    'Curriculum',
    'Category',
    'StudyCycle',
    'Module',
    'Discipline',
    'Course',
    'Term',
    'ClockCell',
)

class AcademHubModel(UrlGenerateMixin, models.Model):
    def get_absolute_url(self):
        url = self.get_urls()['url_detail']
        return reverse(url, kwargs={'pk': self.pk})

    class Meta:
        abstract = True

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

class CustomUserManager(BaseUserManager):
    '''
    Менеджер для пользовательской модели, который управляет созданием пользователей.
    Предоставляет методы для создания обычного пользователя и суперпользователя.
    '''
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)

        full_name = "Admin Admin Admin"

        user = self.model(email=email, full_name=full_name, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AcademHubModel, AbstractBaseUser, PermissionsMixin):
    '''
    Пользовательская модель, представляющая пользователей системы. 
    Наследует от AbstractBaseUser и PermissionsMixin для поддержки аутентификации и управления правами доступа.
    '''
    email = models.EmailField(unique=True, verbose_name='Почта')
    full_name = models.CharField(
        max_length=255,
        verbose_name='ФИО'
    )

    is_active = models.BooleanField(default=True, verbose_name='Активный?')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал?')
    is_teacher = models.BooleanField(default=False, verbose_name='Учитель?')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.full_name


<<<<<<< HEAD
=======
class Discipline(AcademHubModel):
    code = models.CharField(max_length=50, unique=False, verbose_name="Код", blank=True ,null=True)
    name = models.CharField(max_length=255, verbose_name="Наименование")
    specialty = models.ForeignKey(
        'Specialty', on_delete=models.CASCADE, related_name="disciplines", verbose_name="Специальность"
    )

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"

    def __str__(self):
        return self.name


>>>>>>> 1004b84225cea52c0011c4f0be491724a0ebdd2b
class MiddleCertification(AcademHubModel):
    # semester = models.PositiveSmallIntegerField(verbose_name='Семестр')
    SEMESTER_CHOICES = [(i, str(i)) for i in range(1, 8)]

    semester = models.PositiveSmallIntegerField(
        choices=SEMESTER_CHOICES,
        verbose_name='Семестр'
    )
    discipline = models.ForeignKey(
        'Discipline',
        on_delete=models.CASCADE,
        related_name='middle_certifications',
        verbose_name='Дисциплина'
    )
    hours = models.PositiveIntegerField(verbose_name='Часы')
    is_exam = models.BooleanField(default=False, verbose_name='Экзамен')

    class Meta:
        verbose_name = "Промежуточная аттестация"
        verbose_name_plural = "Промежуточные аттестации"

    def __str__(self):
        return f"{self.discipline.name} ({'Экзамен' if self.is_exam else 'Зачет'})"


# class ProfessionalModule(AcademHubModel):
#     module_name = models.CharField(max_length=100, verbose_name="Наименование профессионального модуля")
#     hours = models.PositiveIntegerField(verbose_name='Часы')
#
# class Practice(AcademHubModel):
#     SEMESTER_CHOICES = [(i, str(i)) for i in range(1, 9)]
#     PRACTICE_TYPES = (
#         ('УП', 'Учебная практика'),
#         ('ПП', 'Производственная практика')
#     )
#
#     practice_name = models.CharField(max_length=100, verbose_name='Наименование практики')
#     practice_type = models.CharField(max_length=255, verbose_name="Тип практики", choices=PRACTICE_TYPES)
#     # semester = models.PositiveSmallIntegerField(verbose_name='Семестр')
#     hours = models.PositiveIntegerField(verbose_name='Часы')
#     semester = models.PositiveSmallIntegerField(
#         choices=SEMESTER_CHOICES,
#         verbose_name='Семестр'
#     )

class ProfessionalModule(AcademHubModel):

    module_name = models.CharField(max_length=100, verbose_name="Наименование профессионального модуля")
    discipline = models.OneToOneField(
        'Discipline',
        on_delete=models.CASCADE,
        related_name='prof_modules',
        verbose_name='Дисциплина'
    )

    def __str__(self):
        return self.module_name

class Practice(AcademHubModel):
    PRACTICE_TYPES = (
        ('УП', 'Учебная практика'),
        ('ПП', 'Производственная практика')
    )
    practice_name = models.CharField(max_length=100, verbose_name='Наименование практики')
    practice_type = models.CharField(max_length=255, verbose_name="Тип практики", choices=PRACTICE_TYPES)

    discipline = models.OneToOneField(
        'Discipline',
        on_delete=models.CASCADE,
        related_name='practices',
        verbose_name='Дисциплина'
    )

    def __str__(self):
        return self.practice_name

class TermPaper(AcademHubModel):

    name = models.CharField(max_length=255, verbose_name="Название курсового проекта", default="Курсовой проект")

    discipline = models.OneToOneField(
        'Discipline',
        on_delete=models.CASCADE,
        related_name='term_papers',
        verbose_name='Дисциплина'
    )

    def __str__(self):
        return self.name



class Specialty(AcademHubModel):
    '''
        09.02.07
    '''

    code = models.CharField(max_length=50, unique=True, verbose_name="Код")
    name = models.CharField(max_length=255, verbose_name="Наименование")
    name = models.CharField(max_length=255, verbose_name="Наименование")


    class Meta:
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"

    def __str__(self):
        return self.name

class Qualification(AcademHubModel):
    '''
        Программист
        Веб дизайнер
        и т.д
    '''

    short_name = models.CharField(max_length=50, verbose_name="Сокращенное название")
    name = models.CharField(max_length=255, verbose_name="Наименование")
    specialty = models.ForeignKey(
        Specialty, on_delete=models.CASCADE, related_name="qualifications", null=True, verbose_name="Специальность"
    )

    class Meta:
        verbose_name = "Квалификация"
        verbose_name_plural = "Квалификации"

    def __str__(self):
        return self.name


class Curriculum(models.Model):
    qualification = models.ForeignKey(
        Qualification,
        on_delete=models.CASCADE,
        verbose_name="Квалификация"
    )
    admission_year = models.PositiveIntegerField(verbose_name="Год поступления")

    class Meta:
        verbose_name = "Учебный план"
        verbose_name_plural = "Учебные планы"
        unique_together = ['qualification', 'admission_year']

    def __str__(self):
        return f"План для {self.qualification} ({self.admission_year} года)"


class GroupStudents(AcademHubModel):
    '''
        П50-9-21
    '''

    EDUCATION_BASE_CHOICES = (
        ("Основное общее", "Основное общее"),
        ("Среднее общее", "Среднее общее"),
    )

    COURCE_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4')
    )

    def get_years_choices():
        years = []
        for i in range(1990, timezone.now().year + 1):
            years.append((i, i))
        return years

    def get_default_number_value(self):
        return GroupStudents.objects.filter(
            year_create=self.year_create,
            qualification=self.qualification,
        ).count() + 1

    full_name = models.CharField(blank=True, null=True, verbose_name='Полное название группы', max_length=1000,
                                 unique=True)

    qualification = models.ForeignKey(
        Qualification, on_delete=models.CASCADE, related_name="groups", verbose_name="Квалификация"
    )

    number = models.PositiveIntegerField(
        verbose_name='Порядковый номер группы в потоке',
    )

    education_base = models.CharField(
        max_length=255,
        verbose_name="База образования",
        choices=EDUCATION_BASE_CHOICES,
        default=EDUCATION_BASE_CHOICES[0][1]
    )

    year_create = models.PositiveIntegerField(
        verbose_name='Год создания',
        choices=get_years_choices(),
        default=timezone.now().year
    )

    current_course = models.IntegerField(
        verbose_name="Курс",
        choices=COURCE_CHOICES,
        default=COURCE_CHOICES[0][1],
        null=False
    )

    is_active = models.BooleanField(null=True, blank=True, default=True, verbose_name="Активная группа")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.number = self.get_default_number_value()

        if self.education_base != "Основное общее":
            self.full_name = f"{self.qualification.short_name}-11/{self.number}-{str(self.year_create)[-2:]}"
        else:
            self.full_name = f"{self.qualification.short_name}-{self.number}-{str(self.year_create)[-2:]}"

        return super().save(*args, **kwargs)


class CalendarGraphicOfLearningProcess(AcademHubModel):

    name = models.CharField(max_length=255, verbose_name="Название")

    group = models.ForeignKey(
        GroupStudents,
        on_delete=models.CASCADE,
        related_name="learning_process_calendars",
        verbose_name="Группа"
    )

    start_exam_date_first_semester = models.DateField(null=False, blank=False, verbose_name="Дата начала сессии первого семестра")
    date_of_pm_first_semester = models.DateField(null=True, blank=True, verbose_name="Дата экзамена по профессиональному модулю первого семестра")
    start_exam_date_second_semester = models.DateField(null=False, blank=False, verbose_name="Дата начала сессии второго семестра")
    date_of_pm_second_semester = models.DateField(null=True, blank=True, verbose_name="Дата экзамена по профессиональному модулю второго семестра")

    @property
    def all_practice_dates(self):
        return self.practice_dates.select_related('curriculum_item__practice')

    class Meta:
        verbose_name = "Календарный график учебного процесса"
        verbose_name_plural = "Календарные графики учебного процесса"

    def __str__(self):
        return self.name



#
###  Curriculum
#


class Curriculum(AcademHubModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    qualification = models.CharField(max_length=255, null=True)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)

    qualification = models.ForeignKey(
        Qualification,
        on_delete=models.CASCADE,
        verbose_name="Квалификация"
    )
    admission_year = models.PositiveIntegerField(verbose_name="Год поступления")

    class Meta:
        verbose_name = "Учебный план"
        verbose_name_plural = "Учебные планы"
        unique_together = ['qualification', 'admission_year']

    def __str__(self):
        return f"REFACTORED StudyPlan: {self.qualification} ({self.admission_year})"


class Category(AcademHubModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    identificator = models.CharField(max_length=50)
    cycles = models.CharField(max_length=255)
    curriculum = models.ForeignKey(Curriculum, related_name='categoreies', on_delete=models.CASCADE)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return f"{self.identificator} - {self.cycles}"


class StudyCycle(AcademHubModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    identificator = models.CharField(max_length=50)
    cycles = models.CharField(max_length=255)
    categories = models.ForeignKey(Category, related_name='study_cycles', on_delete=models.CASCADE)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Образовательный цикл"
        verbose_name_plural = "Образовательный циклы"

    def __str__(self):
        return f"{self.identificator} - {self.cycles}"


class Module(AcademHubModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    discipline = models.CharField(max_length=255)
    code_of_discipline = models.CharField(max_length=50)
    code_of_cycle_block = models.CharField(max_length=50)
    study_cycles = models.ForeignKey(StudyCycle, related_name='modules', on_delete=models.CASCADE)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"

    def __str__(self):
        return f"{self.code_of_discipline} - {self.discipline}"


class Discipline(AcademHubModel):

    # TYPE_CHOICES = [
    #     ("Профессиональный модуль", "Профессиональный модуль"),
    #     ("Учебная практика", "Учебная практика"),
    #     ("Производственная практика", "Производственная практика"),
    #     ("Курсовая работа", "Курсовая работа")
    # ]
    #
    # type = models.CharField(verbose_name="Тип дисциплины", max_length=255, choices=TYPE_CHOICES)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=50, unique=False, verbose_name="Код", blank=True ,null=True)
    name = models.CharField(max_length=255, verbose_name="Наименование")
    specialty = models.ForeignKey(
        'Specialty', on_delete=models.CASCADE, related_name="disciplines", verbose_name="Специальность"
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="disciplines")
    curriculums = models.ManyToManyField(Curriculum, related_name='children_strings')
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"

    def __str__(self):
        return self.name   


###


# Модель для учебного плана (связывает дисциплины с группами по квалификации и году поступления)
class CurriculumItem(models.Model):
    """
    Сводная таблица для хранения компонентов учебного плана: дисциплин, практик, модулей и курсовых.
    """
    TYPE_CHOICES = (
        ('discipline', 'Дисциплина'),
        ('practice', 'Практика'),
        ('professional_module', 'Профессиональный модуль'),
        ('term_paper', 'Курсовая работа'),
    )

    SEMESTER_CHOICES = [(i, str(i)) for i in range(1, 8)]
    ATTESTATION_CHOICES = (
        ('exam', 'Экзамен'),
        ('credit', 'Зачёт'),
        ('none', 'Без аттестации'),  # Для практик или модулей без формы аттестации
        ('course_pr', 'Защита курсового проекта')
    )

    curriculum = models.ForeignKey(
        'Curriculum',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Учебный план"
    )
    item_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Тип элемента"
    )
    discipline = models.ForeignKey(
        'Discipline',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Дисциплина"
    )
    practice = models.ForeignKey(
        'Practice',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Практика"
    )
    professional_module = models.ForeignKey(
        'ProfessionalModule',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Профессиональный модуль"
    )
    term_paper = models.ForeignKey(
        'TermPaper',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Курсовая работа"
    )
    semester = models.PositiveSmallIntegerField(
        choices=SEMESTER_CHOICES,
        verbose_name="Семестр",
        default=SEMESTER_CHOICES[0][1]
        # null=True,
        # blank=True  # Для курсовых может не быть семестра
    )
    hours = models.PositiveIntegerField(
        verbose_name="Количество часов",
        null=True,
        blank=True  # Для курсовых часов может не быть
    )
    attestation_form = models.CharField(
        max_length=50,
        choices=ATTESTATION_CHOICES,
        verbose_name="Форма аттестации",
        default='none'
    )

    practice_dates = models.ManyToManyField(
        CalendarGraphicOfLearningProcess,
        through='PracticeDate',
        related_name='related_practices',
        verbose_name="Календарные графики"
    )

    class Meta:
        verbose_name = "Элемент учебного плана"
        verbose_name_plural = "Элементы учебного плана"

    def __str__(self):
        if self.item_type == 'discipline' and self.discipline:
            return f"{self.discipline.name} ({self.get_attestation_form_display()})"
        elif self.item_type == 'practice' and self.practice:
            return f"{self.practice.practice_name} ({self.get_attestation_form_display()})"
        elif self.item_type == 'professional_module' and self.professional_module:
            return f"{self.professional_module.module_name} ({self.get_attestation_form_display()})"
        elif self.item_type == 'term_paper' and self.term_paper:
            return f"Курсовая по {self.term_paper.name} ({self.get_attestation_form_display()})"
        return "Неопределённый элемент"

    # def clean(self):
    #     super().clean()  # Вызов метода родительского класса
    #
    #     # если тип элемента - курсовая работа
    #     if self.item_type == 'term_paper':
    #         # Если семестр не пустой, то добавляем ошибку валидации
    #         if self.semester is not None:
    #             raise ValidationError({'semester': "Семестр не должен быть указан для курсовых работ."})
    #     else:
    #         # Для других типов элементов семестр должен быть указан
    #         if self.semester is None:
    #             raise ValidationError({'semester': "Семестр обязателен для данного типа элемента."})



class RecordBookTemplate(models.Model):
    qualification = models.ForeignKey(
        'Qualification',
        on_delete=models.CASCADE,
        verbose_name="Квалификация"
    )
    admission_year = models.PositiveIntegerField(verbose_name="Год поступления")
    student_name = models.CharField(max_length=255, verbose_name="ФИО студента", blank=True)
    record_book_number = models.CharField(max_length=50, verbose_name="Номер зачетной книжки", blank=True)
    admission_order = models.CharField(max_length=100, verbose_name="Приказ о зачислении", blank=True)
    issue_date = models.DateField(verbose_name="Дата выдачи", null=True, blank=True)

    # Связь с учебным планом для дисциплин
    curriculum = models.ForeignKey(
        'Curriculum',
        on_delete=models.CASCADE,
        verbose_name="Учебный план"
    )

    # ManyToMany для различных компонентов зачетки
    middle_certifications = models.ManyToManyField(
        'MiddleCertification',
        verbose_name="Промежуточные аттестации",
        blank=True
    )
    professional_modules = models.ManyToManyField(
        'ProfessionalModule',
        verbose_name="Профессиональные модули",
        blank=True
    )
    practices = models.ManyToManyField(
        'Practice',
        verbose_name="Практики",
        blank=True
    )
    term_papers = models.ManyToManyField(
        'TermPaper',
        verbose_name="Курсовые работы",
        blank=True
    )

    class Meta:
        verbose_name = "Шаблон зачетной книжки"
        verbose_name_plural = "Шаблоны зачетных книжек"
        unique_together = ['qualification', 'admission_year']

    def __str__(self):
        return f"Шаблон для {self.qualification} ({self.admission_year})"



class Student(AcademHubModel):
    EDUCATION_BASE_CHOICES = (
        ("Основное общее", "Основное общее"),
        ("Среднее общее", "Среднее общее"),
    )

    EDUCATION_BASIS_CHOICES = (
        ("Бюджет", 'Бюджет'),
        ("Внебюджет", "Внебюджет")
    )

    REASONS_OF_EXPELLING_CHOICES = (
        ("с/ж", "с/ж"),
        ("Перевод", "Перевод"),
        ("Смерть", "Смерть"),
        ("Окончание обучения", "Окончание обучения")
        #TODO: Выяснить про другие причины
    )

    REASONS_OF_ACADEM_CHOICES = (
        ("с/о", "с/о"),
        ("Смерть", "Смерть"),
        # TODO: Выяснить про другие причины
    )

    full_name = models.CharField(
        max_length=255, 
        verbose_name="ФИО", 
        validators=[validate_full_name]
    )
    phone = models.CharField(max_length=18, verbose_name="Телефон")
    birth_date = models.DateField(verbose_name="Дата рождения")
    snils = models.CharField(max_length=14, verbose_name="СНИЛС")
    group = models.ForeignKey(
        'GroupStudents', on_delete=models.CASCADE, related_name="students", verbose_name="Группа"
    )
    admission_order = models.CharField(max_length=255, verbose_name="Приказ о зачислении") # TODO: Приказ о приеме
    transfer_to_2nd_year_order = models.CharField(max_length=255, verbose_name="Переводной приказ на 2 курс", blank=True, null=True) # TODO: Приказ о переводе на 2 курс
    transfer_to_3rd_year_order = models.CharField(max_length=255, verbose_name="Переводной приказ на 3 курс", blank=True, null=True) # TODO: Приказ о переводе на 3 курс
    transfer_to_4th_year_order = models.CharField(max_length=255, verbose_name="Переводной приказ на 4 курс", blank=True, null=True) # TODO: Приказ о переводе на 4 курс
    academ_order = models.CharField(max_length=255, verbose_name="Приказ об уходе в академический отпуск", blank=True, null=True) # TODO: Приказ об уходе в академ
    expell_order = models.CharField(max_length=255, verbose_name="Приказ об отчислении", blank=True, null=True) # TODO: Приказ об отчислении
    reinstaitment_order = models.CharField(max_length=255, verbose_name="Приказ о восстановлении", blank=True, null=True) # TODO: Приказ о восстановлении
    expelled_due_to_graduation = models.BooleanField(verbose_name="Отчислен в связи с окончанием обучения", blank=True, null=True, default=False)
    education_base = models.CharField(max_length=255, verbose_name="База образования", choices=EDUCATION_BASE_CHOICES, default=EDUCATION_BASE_CHOICES[0][1])
    education_basis = models.CharField(max_length=255, verbose_name="Основа образования", choices=EDUCATION_BASIS_CHOICES, default=EDUCATION_BASIS_CHOICES[0][1])
    registration_address = models.TextField(verbose_name="Адрес прописки")
    actual_address = models.TextField(verbose_name="Адрес фактический")
    representative_full_name = models.CharField(
        max_length=255, 
        verbose_name="ФИО представителя", 
        # validators=[validate_full_name]
    )
    representative_email = models.EmailField(
        verbose_name="Почта представителя", 
        # validators=[validate_email]
    )
    note = models.TextField(blank=True, null=True, verbose_name="Примечание")
    left_course = models.IntegerField(blank=True, null=True, verbose_name="Курс, с которого ушел")
    reason_of_expelling = models.CharField(max_length=255, verbose_name="Причина отчисления", blank=True, null=True, choices=REASONS_OF_EXPELLING_CHOICES)

    is_in_academ = models.BooleanField(verbose_name="Находится ли студент в академе", default=False, blank=True, null=True)
    reason_of_academ = models.CharField(max_length=255, verbose_name="Причина ухода в академ", blank=True, null=True, choices=REASONS_OF_ACADEM_CHOICES)
    record_book = models.OneToOneField('StudentRecordBook', on_delete=models.SET_NULL, null=True, blank=True,
                                       verbose_name="Зачётная книжка", related_name="student_record_book")
    academ_leave_date = models.DateField(null=True, blank=True, verbose_name="Дата ухода в академ")
    academ_return_date = models.DateField(null=True, blank=True, verbose_name="Дата возвращения из академа")

    date_of_expelling = models.DateField(null=True, blank=True, verbose_name="Дата отчисления")
    is_expelled = models.BooleanField(null=True, blank=True, default=False, verbose_name="Отчислен ли студент")
    ancete_number = models.CharField(max_length=30, verbose_name="Номер анкеты абитуриента", blank=True, null=True)
    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
        permissions = [
            ('import_student', 'Import student'),
            ('academic_come_back_student', 'Come back student from academic'),
            ('academic_leave_student', 'May send academic leave'),
            ('expel_student', 'Expel student'),
            ('generate_record_book,student', 'Generate record book')
        ]

    def save(self, *args, **kwargs):
        from django.utils import timezone  # Импортируем внутри метода, чтобы избежать проблем с импортом
        from django.core.exceptions import ValidationError

        # Проверка соответствия education_base группы и студента
        if self.group and self.education_base != self.group.education_base:
            raise ValidationError(
                f"База образования студента ({self.education_base}) не соответствует "
                f"базе образования группы ({self.group.education_base})"
            )

        # Сохраняем старые значения перед обновлением
        if self.pk:  # Если это обновление существующего объекта
            old_student = Student.objects.get(pk=self.pk)
            old_group = old_student.group.full_name if old_student.group else None
            old_is_in_academ = old_student.is_in_academ
            old_is_expelled = old_student.is_expelled
        else:
            old_group = None
            old_is_in_academ = False
            old_is_expelled = False

        # Сохраняем объект
        super().save(*args, **kwargs)

        # Проверяем изменения и создаём записи в ContingentMovement
        current_group = self.group.full_name if self.group else None

        # 1. Перевод в другую группу
        if old_group and old_group != current_group:
            ContingentMovement.objects.create(
                order_number=self.reinstaitment_order if self.reinstaitment_order else f"TR-{self.pk}-{timezone.now().strftime('%Y%m%d')}",
                action_type='transfer',
                action_date=timezone.now().date(),
                previous_group=old_group,
                new_group=current_group,
                student=self
            )

        # 2. Уход в академический отпуск
        if not old_is_in_academ and self.is_in_academ:
            ContingentMovement.objects.create(
                order_number=self.academ_order if self.academ_order else f"AL-{self.pk}-{timezone.now().strftime('%Y%m%d')}",
                action_type='academic_leave',
                action_date=self.academ_leave_date or timezone.now().date(),
                previous_group=current_group,
                new_group=current_group,  # Сохраняем текущую группу как возможную для возвращения
                student=self
            )

        # 3. Выход из академического отпуска
        if old_is_in_academ and not self.is_in_academ and self.academ_return_date:
            ContingentMovement.objects.create(
                order_number=self.reinstaitment_order if self.reinstaitment_order else f"AR-{self.pk}-{timezone.now().strftime('%Y%m%d')}",
                action_type='academic_return',
                action_date=self.academ_return_date,
                previous_group=old_group,
                new_group=current_group,
                student=self
            )

        # 4. Отчисление
        if not old_is_expelled and self.is_expelled:
            ContingentMovement.objects.create(
                order_number=self.expell_order if self.expell_order else f"EX-{self.pk}-{timezone.now().strftime('%Y%m%d')}",
                action_type='expulsion',
                action_date=self.date_of_expelling or timezone.now().date(),
                previous_group=current_group,
                new_group=None,  # Новая группа не указывается при отчислении
                student=self
            )

        # 5. Восстановление
        if old_is_expelled and not self.is_expelled and self.reinstaitment_order:
            ContingentMovement.objects.create(
                order_number=self.reinstaitment_order,
                action_type='reinstatement',
                action_date=timezone.now().date(),
                previous_group=None,  # Предыдущая группа не указывается при восстановлении
                new_group=current_group,
                student=self
            )


    @property
    def course(self):
        return self.group.current_course

    def __str__(self):
        return self.full_name

class StudentRecordBook(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, verbose_name="Студент")
    qualification = models.ForeignKey('Qualification', on_delete=models.CASCADE, verbose_name="Квалификация")
    admission_year = models.PositiveIntegerField(verbose_name="Год поступления")
    student_name = models.CharField(max_length=255, verbose_name="ФИО студента", blank=True)
    record_book_number = models.CharField(max_length=50, unique=True, verbose_name="Номер зачётной книжки")
    admission_order = models.CharField(max_length=100, verbose_name="Приказ о зачислении", blank=True)
    issue_date = models.DateField(verbose_name="Дата выдачи", null=True, blank=True)
    curriculum = models.ForeignKey('Curriculum', on_delete=models.CASCADE, verbose_name="Учебный план")
    middle_certifications = models.ManyToManyField('MiddleCertification', verbose_name="Промежуточные аттестации", blank=True)
    professional_modules = models.ManyToManyField('ProfessionalModule', verbose_name="Профессиональные модули", blank=True)
    practices = models.ManyToManyField('Practice', verbose_name="Практики", blank=True)
    term_papers = models.ManyToManyField('TermPaper', verbose_name="Курсовые работы", blank=True)

    class Meta:
        verbose_name = "Зачётная книжка студента"
        verbose_name_plural = "Зачётные книжки студентов"

    def __str__(self):
        return f"Зачётка {self.student_name} ({self.record_book_number})"


class GradebookStudents(AcademHubModel):
    ASSESSMENT_CHOICES = (
        ('Отлично', '5'),
        ('Хорошо', '4'),
        ('Удовлетворительно', '3'),
        ('Неудовлетворительно', '2'),
        ('Неявка', 'Неявка'),
    )

    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        verbose_name='Студент'
    )
    gradebook = models.ForeignKey(
        'Gradebook', 
        on_delete=models.CASCADE,
        verbose_name='Ведомость'
    )
    ticket_number = models.PositiveIntegerField(
        verbose_name='№ билета',
        blank=True,
        null=True
    )
    grade = models.CharField(
        verbose_name='Оценка', 
        choices=ASSESSMENT_CHOICES, 
        default=ASSESSMENT_CHOICES[0][1], 
        max_length=50,
        blank=True
    )

    class Meta:
        verbose_name = "Оценка студента"
        verbose_name_plural = "Оценки студентов"

    def __str__(self):
        return f"{self.student.full_name} - {self.grade}"

class Gradebook(AcademHubModel):
    STATUS_CHOICE = (
        ('Не заполнена', 'Не заполнена'),
        ('Открыта', 'Открыта'),
        ('Заполнена', "Заполнена"),
        ('Закрыта', 'Закрыта'),
        ('Просрочена', "Просрочена")
    )

    SEMESTER_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
    )

    NAME_CHOICES = (
        ("Экзаменационная ведомость", "Экзаменационная ведомость"),
        ("Ведомость защиты курсового проекта", "Ведомость защиты курсового проекта"),
        ("Ведомость дифференцированного зачета", "Ведомость дифференцированного зачета"),
        ("Ведомость результатов демонстрационного экзамена", "Ведомость результатов демонстрационного экзамена"),
        ("Ведомость успеваемости", "Ведомость успеваемости")
    )

    TYPE_CHOICES = (
        ("Первичная сдача", "Первичная сдача"),
        ("Пересдача", "Пересдача"),
        ("Комиссия", "Комиссия")
    )

    number = models.CharField(
        max_length=255,
        verbose_name='Номер ведомости'
    )

    date_of_opening = models.DateField(verbose_name="Дата открытия ведомости", blank=True, null=True)
    date_of_filling = models.DateField(blank=True, null=True, verbose_name="Дата заполнения ведомости")
    date_of_closing = models.DateField(blank=True, null=True, verbose_name="Дата закрытия ведомости")
    amount_of_days_for_closing = models.PositiveIntegerField(verbose_name="Сколько дней дается на закрытие ведомости с момента открытия", blank=True, null=True)

    type_of_grade_book = models.CharField(blank=True, null=True, verbose_name="Тип ведомости", choices=TYPE_CHOICES, max_length=255)

    teachers = models.ManyToManyField(
        'CustomUser', 
        verbose_name="Преподаватели"
    )
    group = models.ForeignKey(
        GroupStudents, 
        on_delete=models.CASCADE, 
        related_name="gradebooks",
        verbose_name="Группа"
    )
    students = models.ManyToManyField(
        Student, verbose_name="Студенты", related_name="gradebooks", through=GradebookStudents
    )
    name = models.CharField(max_length=255, verbose_name="Наименование ведомости", choices=NAME_CHOICES, default=NAME_CHOICES[0][1])
    discipline = models.ForeignKey(
        'Discipline', on_delete=models.CASCADE, related_name="gradebooks", verbose_name="Дисциплина"
    )
    status = models.CharField(
        max_length=50, 
        verbose_name="Статус",
        choices=STATUS_CHOICE,
        default=STATUS_CHOICE[0][0], 
        blank=False)
    semester_number = models.IntegerField(verbose_name="Номер семестра", choices=SEMESTER_CHOICES, default=SEMESTER_CHOICES[0][1])

    generated = models.BooleanField(verbose_name="Была ли ведомсть сгенерирована", default=False, null=False, blank=False)

    class Meta:
        verbose_name = "Ведомость"
        verbose_name_plural = "Ведомости"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Автоматически генерирует номер ведомости при создании.
        """
        if not self.number:  # Если номер не задан
            settings = ProgramSettings.get_current_settings()
            settings.reset_counter_if_august()  # Проверяем, нужно ли сбросить счетчик
            settings.reset_year_if_new() # Проверяем, нужно ли обновить год
            settings.increment_counter()
            self.number = settings.generate_gradebook_number()
        super().save(*args, **kwargs)



class ContingentMovement(AcademHubModel):
    """
    Модель для отслеживания движения контингента: переводы, отчисления, академические отпуска.
    """
    ACTION_TYPES = (
        ('transfer', 'Перевод'),
        ('expulsion', 'Отчисление'),
        ('academic_leave', 'Уход в академический отпуск'),
        ('academic_return', 'Выход из академического отпуска'),
        ('reinstatement', 'Восстановление'),
    )

    order_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Номер приказа"
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name="Тип действия"
    )
    action_date = models.DateField(
        verbose_name="Дата действия"
    )
    previous_group = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Предыдущая группа"
    )
    new_group = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Новая группа"
    )
    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name="movements",
        verbose_name="Студент"
    )

    class Meta:
        verbose_name = "Движение контингента"
        verbose_name_plural = "Движения контингента"
        ordering = ['-action_date']  # Сортировка по убыванию даты действия

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.student.full_name} ({self.action_date})"
    


"""
#
## Здесь все таблицы относящиеся к учебному плану
#
"""


class Course(AcademHubModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    course_number = models.IntegerField()
    module = models.ForeignKey(Module, related_name='courses', on_delete=models.CASCADE, null=True)
    disipline = models.ForeignKey(Discipline, related_name='courses', on_delete=models.CASCADE, null=True)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return f"Курс {self.course_number}"

class Term(AcademHubModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    term_number = models.IntegerField()
    course = models.ForeignKey(Course, related_name='terms', on_delete=models.CASCADE)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Семестр"
        verbose_name_plural = "Семестры"

    def __str__(self):
        return f"Семестр {self.term_number}"

class ClockCell(AcademHubModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code_of_type_work = models.CharField(max_length=100)
    code_of_type_hours = models.CharField(max_length=100)
    course = models.IntegerField()
    term = models.IntegerField()
    count_of_clocks = models.IntegerField()
    term_relation = models.ForeignKey(Term, related_name='clock_cells', on_delete=models.CASCADE)
    warnings = models.BooleanField(default=False)
    warning_description = models.JSONField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Ячейка часов"
        verbose_name_plural = "Ячейки часов"

    def __str__(self):
        return f"{self.code_of_type_work} - {self.count_of_clocks} часов"

def validate_practice_dates(value):
    if value.start_date > value.end_date:
        raise ValidationError("Дата окончания не может быть раньше даты начала")

class PracticeDate(AcademHubModel):
    calendar_graphic = models.ForeignKey(
        CalendarGraphicOfLearningProcess,
        on_delete=models.CASCADE,
        related_name='practice_dates',
        verbose_name="Календарный график"
    )

    curriculum_item = models.ForeignKey(
        CurriculumItem,
        on_delete=models.CASCADE,
        limit_choices_to={'item_type': 'practice'},
        verbose_name="Практика из учебного плана"
    )

    start_date = models.DateField(verbose_name="Дата начала практики")
    end_date = models.DateField(verbose_name="Дата окончания практики")

    class Meta:
        verbose_name = "Дата практики"
        verbose_name_plural = "Даты практик"
        unique_together = [['calendar_graphic', 'curriculum_item']]

    def __str__(self):
        return f"{self.curriculum_item} ({self.start_date} - {self.end_date})"

    def clean(self):
        validate_practice_dates(self)

from django.db import models
from django.utils import timezone

def get_current_year():
    return timezone.now().year

class ProgramSettings(models.Model):
    """
    Модель для хранения настроек программы.
    """
    gradebook_prefix = models.CharField(
        max_length=50,
        verbose_name="Префикс номера ведомости",
        default="18.01",  # По умолчанию "ВДМ"
        help_text="Префикс, с которого начинается номер ведомости."
    )
    current_year = models.PositiveIntegerField(
        verbose_name="Текущий год",
        default=get_current_year,  # Используем функцию вместо лямбды
        help_text="Текущий год для формирования номера ведомости."
    )
    gradebook_counter = models.PositiveIntegerField(
        verbose_name="Счетчик ведомостей",
        default=0,  # Начинаем с нуля
        help_text="Счетчик ведомостей, который сбрасывается каждый август."
    )

    class Meta:
        verbose_name = "Настройки программы"
        verbose_name_plural = "Настройки программы"

    def __str__(self):
        return f"Настройки: {self.gradebook_prefix}-{self.current_year % 100}/XXXX"

    def reset_counter(self):
        """
        Сбрасывает счетчик ведомостей.
        """
        self.gradebook_counter = 0
        self.save()

    def reset_year(self):
        """
        Обновляет год
        """
        self.year = timezone.now().year
        self.save()

    def increment_counter(self):
        """
        Увеличивает счетчик ведомостей на 1.
        """
        self.gradebook_counter += 1
        self.save()

    def generate_gradebook_number(self):
        """
        Генерирует номер ведомости по шаблону: <префикс><год>/<счетчик>.
        """
        year_short = self.current_year % 100  # Последние две цифры года
        return f"{self.gradebook_prefix}-{year_short:02d}/{self.gradebook_counter:04d}"

    @classmethod
    def get_current_settings(cls):
        """
        Возвращает текущие настройки программы.
        Если настройки отсутствуют, создает новую запись.
        """
        settings, created = cls.objects.get_or_create(pk=1)  # Единая запись с ID=1
        return settings

    @classmethod
    def reset_counter_if_august(cls):
        """
        Сбрасывает счетчик ведомостей, если начался август.
        """
        current_month = timezone.now().month
        settings = cls.get_current_settings()

        if current_month == 8:
            settings.reset_counter()


    @classmethod
    def reset_year_if_new(cls):
        """
        Обновляет год, если сейчас уже новый год
        """
        current_year = timezone.now().year
        settings = cls.get_current_settings()
        if current_year != settings.current_year:
            settings.reset_counter()