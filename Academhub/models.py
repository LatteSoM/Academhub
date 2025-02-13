from datetime import datetime

from django.db import models
from Academhub.validators import *
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission, Group

__all__ = {
    'AcademHubModel',
    'CustomUser',
    'GroupStudents',
    'Discipline',
    'Specialty',
    'Qualification',
    'Student',
    'Gradebook',
}


url_attrs = [
    'list',
    'delete',
    'create',
    'update',
    'detail',
]

class UrlGenerateMixin:
    _urls = None

    @classmethod
    def _generate_url(cls):
        cls._urls = {}
        
        for attr in url_attrs:
            prefix_name = 'url_' + attr
            cls._urls[prefix_name] = f'{cls.__name__.lower()}_{attr}'

        return cls._urls
    
    @classmethod
    def _check_urls(cls):
        if not cls._urls:
            cls._generate_url()

    @classmethod
    def get_urls(cls):
        cls._check_urls()
        return cls._urls

    @classmethod
    def set_url(cls, name):
        cls._check_urls()
        cls._urls[name] = name

class AcademHubModel(models.Model, UrlGenerateMixin):
    def get_absolute_url(self):
        url = self.get_urls()['url_detail']
        return reverse(url, kwargs={'pk': self.pk})
    
    class Meta:
        abstract = True

class CustomUserManager(BaseUserManager):
    '''
    Менеджер для пользовательской модели, который управляет созданием пользователей.
    Предоставляет методы для создания обычного пользователя и суперпользователя.
    '''
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

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
    email = models.EmailField(unique=True)
    full_name = models.CharField(
        max_length=255,
        verbose_name='ФИО'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активный?')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал?')
    is_teacher = models.BooleanField(default=False, verbose_name='Учитель?')
    is_superuser = models.BooleanField(default=False, verbose_name='Суперпользователь?')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def has_perm(self, perm, obj = ...):
        print(perm)
        return super().has_perm(perm, obj)

    def __str__(self):
        return self.full_name

class PermissionProxy(Permission, UrlGenerateMixin):
    '''
        Расширение для модели Permissions. Поддерживает навигацию
    '''
    
    def get_absolute_url(self):
        url = self.get_urls()['url_detail']
        return reverse(url, kwargs={'pk': self.pk})

    class Meta:
        proxy = True
        ordering = ['pk']
        verbose_name = 'Право'
        verbose_name_plural = 'Права'

class GroupProxy(Group, UrlGenerateMixin):
    '''
        Расширение для модели Group. Поддерживает навигацию
    '''
    
    def get_absolute_url(self):
        url = self.get_urls()['url_detail']
        return reverse(url, kwargs={'pk': self.pk})

    class Meta:
        proxy = True
        verbose_name = 'Группа прав'
        verbose_name_plural = 'Группы прав'

class Discipline(AcademHubModel):
    code = models.CharField(max_length=50, unique=True, verbose_name="Код")
    name = models.CharField(max_length=255, verbose_name="Наименование")
    specialty = models.ForeignKey(
        'Specialty', on_delete=models.CASCADE, related_name="disciplines", verbose_name="Специальность"
    )

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"

    def __str__(self):
        return self.name

class Specialty(AcademHubModel):

    code = models.CharField(max_length=50, unique=True, verbose_name="Код")
    name = models.CharField(max_length=255, verbose_name="Наименование")

    class Meta:
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"

    def __str__(self):
        return self.name

class Qualification(AcademHubModel):

    short_name = models.CharField(max_length=50, verbose_name="Сокращенное название")
    name = models.CharField(max_length=255, verbose_name="Наименование")
    specialty = models.ForeignKey(
        Specialty, on_delete=models.CASCADE, related_name="qualifications", verbose_name="Специальность"
    )

    class Meta:
        verbose_name = "Квалификация"
        verbose_name_plural = "Квалификации"

    def __str__(self):
        return self.name

class GroupStudents(AcademHubModel):

    number = models.CharField(max_length=50, unique=True, verbose_name="Номер")
    qualification = models.ForeignKey(
        Qualification, on_delete=models.CASCADE, related_name="groups", verbose_name="Квалификация"
    )

    EDUCATION_BASE_CHOICES = (
        ("Основное общее", "Основное общее"),
        ("Среднее общее", "Среднее общее"),
    )

    COURCE_CHOICES = (
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4')
    )

    education_base = models.CharField(
        max_length=255,
        verbose_name="База образования",
        choices=EDUCATION_BASE_CHOICES,
        default=EDUCATION_BASE_CHOICES[0][1]
    )

    date_of_creation = models.DateField(
        auto_now=True,
        verbose_name="Дата создания"
    )

    current_course = models.IntegerField(
        verbose_name="Курс",
        choices=COURCE_CHOICES,
        default=COURCE_CHOICES[0][1],
        null=False
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.number

class Student(AcademHubModel):
    # COURSE_CHOICES = (
    #     (1, 1),
    #     (2, 2),
    #     (3, 3),
    #     (4, 4)
    # )

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
        #TODO: Выяснить про другие причины
    )

    full_name = models.CharField(max_length=255, verbose_name="ФИО", validators=[validate_full_name])
    phone = models.CharField(max_length=15, verbose_name="Телефон", validators=[validate_phone])
    birth_date = models.DateField(verbose_name="Дата рождения")
    snils = models.CharField(max_length=14, 
        verbose_name="СНИЛС", 
        validators=[validate_snils]
    )
    # course = models.IntegerField(
    #     verbose_name="Курс",
    #     choices=COURSE_CHOICES,
    #     default=COURSE_CHOICES[0][1]
    # )
    group = models.ForeignKey(
        GroupStudents, on_delete=models.CASCADE, related_name="students", verbose_name="Группа"
    )
    admission_order = models.CharField(
        max_length=255, verbose_name="Приказ о зачислении"
    )
    transfer_to_2nd_year_order = models.CharField(
        max_length=255, verbose_name="Переводной приказ на 2 курс", blank=True, null=True
    )
    transfer_to_3rd_year_order = models.CharField(
        max_length=255, verbose_name="Переводной приказ на 3 курс", blank=True, null=True
    )
    transfer_to_4th_year_order = models.CharField(
        max_length=255, verbose_name="Переводной приказ на 4 курс", blank=True, null=True
    )
    expelled_due_to_graduation = models.CharField(
        default=False, max_length=255, verbose_name="Отчислен в связи с окончанием обучения",
    blank=True, null=True)

    education_base = models.CharField(
        max_length=255, 
        verbose_name="База образования",
        choices=EDUCATION_BASE_CHOICES,
        default=EDUCATION_BASE_CHOICES[0][1]
    )
    education_basis = models.CharField(
        max_length=255, 
        verbose_name="Основа образования",
        choices=EDUCATION_BASIS_CHOICES,
        default=EDUCATION_BASIS_CHOICES[0][1]
    )
    registration_address = models.TextField(
        verbose_name="Адрес прописки"
    )
    actual_address = models.TextField(
        verbose_name="Адрес фактический"
    )
    representative_full_name = models.CharField(
        max_length=255, verbose_name="ФИО представителя", validators=[validate_full_name]
    )
    representative_email = models.EmailField(
        verbose_name="Почта представителя"
    )
    note = models.TextField(blank=True, null=True, verbose_name="Примечание")
    left_course = models.IntegerField(
        blank=True, null=True, verbose_name="Курс, с которого ушел"
    )

    reason_of_expelling = models.CharField(
        max_length=255,
        verbose_name="Причина отчисления",
        blank=True, null=True,
        choices=REASONS_OF_EXPELLING_CHOICES
    )

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return self.full_name

class GradebookStudents(AcademHubModel):
    ASSESSMENT_CHOICES = (
        ('Не указана', 'Не указана'),
        ('Отлично', '5'),
        ('Хорошо', '4'),
        ('Удовлетворительно', '3'),
        ('Неудовлетворительно', '2'),
        ('Неявка', 'Неявка'),
    )



    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name='Студент',
    )
    gradebook = models.ForeignKey(
        to='Gradebook',
        on_delete=models.CASCADE,
        verbose_name='Ведомость',
    )
    ticket_number = models.PositiveIntegerField(
        verbose_name='Номер билета',
    )
    grade = models.CharField(
        choices=ASSESSMENT_CHOICES,
        verbose_name='Оценка',
        default=ASSESSMENT_CHOICES[0][0],
        max_length=50,
    )

class Gradebook(AcademHubModel):

    STATUS_CHOICE = (
        ('Не заполнен', 'Не заполнен'),
        ('Заполнен', 'Заполнен'),
        ('Закрыта', 'Закрыта'),
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
        ("Ведомость защиты курсовой работы", "Ведомость защиты курсовой работы"),
        ("Зачетная ведомость", "Зачетная ведомость"),
        ("Ведомость результатов демонстрационного экзамена", "Ведомость результатов демонстрационного экзамена"),
        ("Ведомость дифференцированного зачета", "Ведомость дифференцированного зачета"),
        ("Ведомость успеваемости", "Ведомость успеваемости")
    )

    teacher = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name="gradebooks", 
        verbose_name="Преподаватель"
    )

    group = models.ForeignKey(
        GroupStudents, 
        on_delete=models.CASCADE, 
        related_name="gradebooks", 
        verbose_name="Группа",
    )
    students = models.ManyToManyField(
        Student,
        verbose_name="Студенты",
        related_name="gradebooks",
        through=GradebookStudents
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Наименование ведомости",
        choices=NAME_CHOICES,
        default=NAME_CHOICES[0][1]
    )
    discipline = models.ForeignKey(
        Discipline, 
        on_delete=models.CASCADE, 
        related_name="gradebooks", 
        verbose_name="Дисциплина"
    )
    
    status = models.CharField(
        max_length=50,
        verbose_name="Статус", 
        default=STATUS_CHOICE[0][0],
        null=False
    )

    semester_number = models.IntegerField(
        verbose_name="Номер семестра",
        choices=SEMESTER_CHOICES,
        null=False
    )

    class Meta:
        verbose_name = "Ведомость"
        verbose_name_plural = "Ведомости"

    def __str__(self):
        return self.name
