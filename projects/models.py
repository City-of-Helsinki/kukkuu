from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from helsinki_gdpr.models import SerializableMixin
from parler.models import TranslatableModel, TranslatedFields

from common.utils import get_translations_dict


class Project(TranslatableModel, SerializableMixin):
    year = models.PositiveSmallIntegerField(verbose_name=_("year"), unique=True)
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255)
    )
    single_events_allowed = models.BooleanField(
        verbose_name=_("single events allowed"),
        help_text=_("Whether it is allowed to create events outside event groups."),
        default=True,
    )
    enrolment_limit = models.PositiveSmallIntegerField(
        verbose_name=_("enrolment limit"),
        help_text=_(
            "How many times a single user can participate events per year. "
            "Changing this will not affect any existing enrolments."
        ),
        default=settings.KUKKUU_DEFAULT_ENROLMENT_LIMIT,
    )

    serialize_fields = [
        {"name": "year"},
        {"name": "name_with_translations"},
    ]

    objects = SerializableMixin.SerializableManager()

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")
        ordering = ["year"]
        permissions = (
            ("admin", _("Base admin permission")),
            ("publish", _("Can publish events and event groups")),
            ("manage_event_groups", _("Can create, update and delete event groups")),
        )

    @property
    def name_with_translations(self):
        return get_translations_dict(self, "name")

    @classmethod
    def get_permission_codenames(cls):
        return [codename for codename, _ in cls._meta.permissions]

    def __str__(self):
        return f"{self.name} {self.year}".strip()

    def can_user_administer(self, user):
        return user.can_administer_project(self)
