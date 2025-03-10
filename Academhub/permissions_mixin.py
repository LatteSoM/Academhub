from django.db import models
from base.models import AcademHubModel
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import GroupManager, PermissionsMixin

__all__ = (
    'ObjectPermissions',
    'GroupPermissions',
    'ObjectPermissionsMixin'
)

class ObjectPermissions(AcademHubModel):
    name = models.CharField(
        verbose_name="Название",
        max_length=150,
        unique=True
    )
    content_type = models.ManyToManyField(
        ContentType,
        models.CASCADE,
        verbose_name="Модели"
    )
    actions = ArrayField(
        base_field=models.CharField(max_length=30),
    )

    class Meta:
        verbose_name = "Разрешение"
        verbose_name_plural = "Разрешения"

    def __str__(self):
        return self.name

class GroupPermissions(AcademHubModel):
    name = models.CharField(_("name"), max_length=150, unique=True)
    permissions = models.ManyToManyField(
        ObjectPermissions,
        verbose_name=_("permissions"),
        blank=True,
    )

    objects = GroupManager()

    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

class ObjectPermissionsMixin(PermissionsMixin):

    groups = models.ManyToManyField(
        GroupPermissions,
        verbose_name="Группы разршений",
        blank=True,
        related_name="user_set",
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        ObjectPermissions,
        verbose_name="Разорешения",
        blank=True,
        related_name="user_set",
        related_query_name="user",
    )

    class Meta:
        abstract = True
