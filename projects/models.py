from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from helsinki_gdpr.models import SerializableMixin
from parler.models import TranslatableModel, TranslatedFields

from common.models import TranslatableQuerySet
from common.utils import get_translations_dict

from .enums import ProjectPermission


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

    objects = SerializableMixin.SerializableManager().from_queryset(
        TranslatableQuerySet
    )()

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")
        ordering = ["year"]
        default_permissions = []
        permissions = (
            (ProjectPermission.ADMIN.value, _("Base admin permission")),
            (
                ProjectPermission.PUBLISH.value,
                _("Can publish events and event groups"),
            ),
            (
                ProjectPermission.MANAGE_EVENT_GROUPS.value,
                _("Can create, update and delete event groups"),
            ),
            (
                ProjectPermission.SEND_MESSAGE_TO_ALL_IN_PROJECT.value,
                _("Can send messages to all recipients in project"),
            ),
            (
                ProjectPermission.VIEW_FAMILIES.value,
                _("Can view families"),
            ),
        )

    @property
    def name_with_translations(self):
        return get_translations_dict(self, "name")

    @classmethod
    def get_permission_codenames(cls):
        return [codename for codename, _ in cls._meta.permissions]

    def __str__(self):
        name = self.safe_translation_getter("name", any_language=True)
        return f"{name} {self.year}".strip()

    def can_user_administer(self, user):
        return user.can_administer_project(self)
