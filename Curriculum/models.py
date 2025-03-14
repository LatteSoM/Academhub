from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission, Group
from django.contrib.auth.models import PermissionManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from Academhub.base.models import AcademHubModel

# Create your models here.

class UnifiedPermissionsManager(PermissionManager):
    """
    Менеджер для прокси модели Permission.
    """

    def get_queryset(self):
        return super().get_queryset().filter(
            content_type__app_label='Academhub',
        )


class PermissionProxy(AcademHubModel, Permission):
    """
    Прокси-модель для прав доступа, связанных с приложением Academhub.
    """

    class Meta:
        proxy = True
        verbose_name = 'Права доступа'
        verbose_name_plural = 'Права доступа'


class GroupProxy(AcademHubModel, Group):
    """
    Прокси-модель для групп, связанных с приложением Academhub.
    """

    class Meta:
        proxy = True
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер пользователей для модели CustomUser.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и возвращает пользователя с указанным email и паролем.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает и возвращает суперпользователя с указанным email и паролем.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AcademHubModel, AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя для приложения Academhub.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Discipline(AcademHubModel):
    """
    Модель учебной дисциплины.
    """
    name = models.CharField(max_length=255, verbose_name='Название дисциплины')
    # Добавьте другие поля, специфичные для дисциплины

    class Meta:
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'

    def __str__(self):
        return self.name


class MiddleCertification(AcademHubModel):
    """
    Модель промежуточной аттестации.
    """
    name = models.CharField(max_length=255, verbose_name='Название аттестации')
    # Добавьте другие поля, специфичные для аттестации

    class Meta:
        verbose_name = 'Промежуточная аттестация'
        verbose_name_plural = 'Промежуточные аттестации'

    def __str__(self):
        return self.name


class ProfessionalModule(AcademHubModel):
    """
    Модель профессионального модуля.
    """
    name = models.CharField(max_length=255, verbose_name='Название модуля')
    # Добавьте другие поля, специфичные для модуля

    def __str__(self):
        return self.name


class Practice(AcademHubModel):
    """
    Модель практики.
    """
    name = models.CharField(max_length=255, verbose_name='Название практики')
    # Добавьте другие поля, специфичные для практики

    def __str__(self):
        return self.name


class TermPaper(AcademHubModel):
    """
    Модель курсовой работы.
    """
    topic = models.CharField(max_length=255, verbose_name='Тема курсовой работы')
    # Добавьте другие поля, специфичные для курсовой работы

    def __str__(self):
        return self.topic


class Specialty(AcademHubModel):
    """
    Модель специальности.
    """
    code = models.CharField(max_length=20, verbose_name='Код специальности')
    name = models.CharField(max_length=255, verbose_name='Название специальности')
    # Добавьте другие поля, специфичные для специальности

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'

    def __str__(self):
        return f"{self.code} - {self.name}"


class Qualification(AcademHubModel):
    """
    Модель квалификации.
    """
    code = models.CharField(max_length=20, verbose_name='Код квалификации')
    name = models.CharField(max_length=255, verbose_name='Название квалификации')
    # Добавьте другие поля, специфичные для квалификации

    class Meta:
        verbose_name = 'Квалификация'
        verbose_name_plural = 'Квалификации'

    def __str__(self):
        return f"{self.code} - {self.name}"


class CurriculumItem(models.Model):
    """
    Модель элемента учебного плана.
    """
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, verbose_name='Дисциплина', null=True,
                                   blank=True)
    professional_module = models.ForeignKey(ProfessionalModule, on_delete=models.CASCADE,
                                             verbose_name='Профессиональный модуль', null=True, blank=True)
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, verbose_name='Практика', null=True, blank=True)
    term_paper = models.ForeignKey(TermPaper, on_delete=models.CASCADE, verbose_name='Курсовая работа', null=True,
                                    blank=True)
    middle_certification = models.ForeignKey(MiddleCertification, on_delete=models.CASCADE,
                                             verbose_name='Промежуточная аттестация', null=True, blank=True)
    hours = models.PositiveIntegerField(verbose_name='Количество часов')
    term = models.PositiveIntegerField(verbose_name='Семестр')
    # Добавьте другие поля, специфичные для элемента учебного плана

    class Meta:
        verbose_name = 'Элемент учебного плана'
        verbose_name_plural = 'Элементы учебного плана'

    def __str__(self):
        return f"{self.discipline or self.professional_module or self.practice} - {self.hours} часов"


class Curriculum(models.Model):
    """
    Модель учебного плана.
    """
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name='Специальность')
    qualification = models.ForeignKey(Qualification, on_delete=models.CASCADE, verbose_name='Квалификация')
    year_of_admission = models.PositiveIntegerField(verbose_name='Год поступления')
    items = models.ManyToManyField(CurriculumItem, verbose_name='Элементы учебного плана')
    # Добавьте другие поля, специфичные для учебного плана

    class Meta:
        verbose_name = 'Учебный план'
        verbose_name_plural = 'Учебные планы'

    def __str__(self):
        return f"Учебный план для специальности {self.specialty} ({self.year_of_admission})"


class RecordBookTemplate(models.Model):
    """
    Модель шаблона зачетной книжки.
    """
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, verbose_name='Учебный план')
    # Добавьте другие поля, специфичные для шаблона зачетной книжки

    class Meta:
        verbose_name = 'Шаблон зачетной книжки'
        verbose_name_plural = 'Шаблоны зачетных книжек'

    def __str__(self):
        return f"Шаблон зачетной книжки для учебного плана {self.curriculum}"


class GroupStudents(AcademHubModel):
    """
    Модель группы студентов.
    """
    name = models.CharField(max_length=255, verbose_name='Название группы')
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, verbose_name='Учебный план')
    start_date = models.DateField(verbose_name='Дата начала обучения')
    end_date = models.DateField(verbose_name='Дата окончания обучения')
    course_number = models.PositiveIntegerField(verbose_name='Номер курса', default=1)

    def get_years_choices():
        return [(r, r) for r in range(2023, 2031)]

    year = models.IntegerField(_('year'), choices=get_years_choices(), default=timezone.now().year)
    number = models.PositiveIntegerField(verbose_name='Номер приказа', default=1)

    def get_default_number_value(self):
        last_number = GroupStudents.objects.order_by('-number').first()
        return last_number.number + 1 if last_number else 1

    class Meta:
        verbose_name = 'Группа студентов'
        verbose_name_plural = 'Группы студентов'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.get_default_number_value()
        super().save(*args, **kwargs)


class Student(AcademHubModel):
    """
    Модель студента.
    """
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=255, verbose_name='Отчество')
    birth_date = models.DateField(verbose_name='Дата рождения')
    group = models.ForeignKey(GroupStudents, on_delete=models.CASCADE, verbose_name='Группа')
    record_book_number = models.CharField(max_length=20, verbose_name='Номер зачетной книжки')
    # Добавьте другие поля, специфичные для студента

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def save(self, *args, **kwargs):
        if not self.record_book_number:
            # Генерация номера зачетной книжки
            self.record_book_number = f"{self.group.name}-{self.birth_date.year}-{str(self.pk).zfill(4)}"
        super().save(*args, **kwargs)

    def course(self):
        today = timezone.now().date()
        if self.group:
            if self.group.start_date <= today <= self.group.end_date:
                return (today.year - self.group.start_date.year) + 1
        return None

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class StudentRecordBook(models.Model):
    """
    Модель зачетной книжки студента.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент')
    record_book_template = models.ForeignKey(RecordBookTemplate, on_delete=models.CASCADE,
                                              verbose_name='Шаблон зачетной книжки')
    # Добавьте другие поля, специфичные для зачетной книжки

    class Meta:
        verbose_name = 'Зачетная книжка студента'
        verbose_name_plural = 'Зачетные книжки студентов'

    def __str__(self):
        return f"Зачетная книжка студента {self.student}"


class GradebookStudents(AcademHubModel):
    """
    Модель ведомости студентов.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент')
    grade = models.CharField(max_length=5, verbose_name='Оценка')
    # Добавьте другие поля, специфичные для ведомости студентов

    class Meta:
        verbose_name = 'Ведомость студентов'
        verbose_name_plural = 'Ведомости студентов'

    def __str__(self):
        return f"Ведомость студента {self.student}"


class Gradebook(AcademHubModel):
    """
    Модель ведомости.
    """
    curriculum_item = models.ForeignKey(CurriculumItem, on_delete=models.CASCADE, verbose_name='Элемент учебного плана')
    group = models.ForeignKey(GroupStudents, on_delete=models.CASCADE, verbose_name='Группа')
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Преподаватель')
    exam_date = models.DateField(verbose_name='Дата экзамена')
    students = models.ManyToManyField(GradebookStudents, verbose_name='Студенты')
    # Добавьте другие поля, специфичные для ведомости

    class Meta:
        verbose_name = 'Ведомость'
        verbose_name_plural = 'Ведомости'

    def __str__(self):
        return f"Ведомость для {self.curriculum_item} группы {self.group}"


class CalendarGraphicOfLearningProcess(AcademHubModel):
    """
    Модель календарного графика учебного процесса.
    """
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, verbose_name='Учебный план')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    # Добавьте другие поля, специфичные для календарного графика

    class Meta:
        verbose_name = 'Календарный график учебного процесса'
        verbose_name_plural = 'Календарные графики учебного процесса'

    def __str__(self):
        return f"Календарный график для {self.curriculum} ({self.start_date} - {self.end_date})"


class ContingentMovement(AcademHubModel):
    """
    Модель движения контингента.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент')
    order_number = models.CharField(max_length=20, verbose_name='Номер приказа')
    order_date = models.DateField(verbose_name='Дата приказа')
    movement_type = models.CharField(max_length=255, verbose_name='Тип движения')
    # Добавьте другие поля, специфичные для движения контингента

    class Meta:
        verbose_name = 'Движение контингента'
        verbose_name_plural = 'Движения контингента'

    def __str__(self):
        return f"Движение студента {self.student} ({self.movement_type})"
