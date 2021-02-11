from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Project(TranslatableModel):
    year = models.PositiveSmallIntegerField(verbose_name=_("year"), unique=True)
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255)
    )

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")
        ordering = ["year"]
        permissions = (
            ("admin", _("Base admin permission")),
            ("publish", _("Can publish")),
        )

    @classmethod
    def get_permission_codenames(cls):
        return [codename for codename, _ in cls._meta.permissions]

    def __str__(self):
        return f"{self.name} {self.year}".strip()

    def can_user_administer(self, user):
        return user.can_administer_project(self)
