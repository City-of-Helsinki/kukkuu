from hashlib import sha256
from typing import Iterable, Optional

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.models import TimestampedModel, UUIDPrimaryKeyModel
from languages.models import Language
from users.models import Guardian


class ChildQuerySet(models.QuerySet):
    def user_can_view(self, user):
        return self.filter(
            Q(guardians__user=user) | Q(project__in=user.administered_projects)
        ).distinct()

    def user_can_update(self, user):
        return self.filter(guardians__user=user)

    def user_can_delete(self, user):
        return self.filter(guardians__user=user)

    @transaction.atomic()
    def delete(self):
        for child in self:
            child.delete()


postal_code_validator = RegexValidator(
    regex=r"^\d{5}$", message="Postal code must be 5 digits", code="invalid_postal_code"
)


class Child(UUIDPrimaryKeyModel, TimestampedModel):
    name = models.CharField(verbose_name=_("name"), max_length=64, blank=True)
    birthyear = models.DateField(verbose_name=_("birthyear"))
    postal_code = models.CharField(
        verbose_name=_("postal code"),
        max_length=5,
        validators=[postal_code_validator],
    )
    guardians = models.ManyToManyField(
        Guardian,
        verbose_name=_("guardians"),
        related_name="children",
        through="children.Relationship",
        blank=True,
    )
    project = models.ForeignKey(
        "projects.Project",
        verbose_name=_("project"),
        related_name="children",
        on_delete=models.PROTECT,
    )
    languages_spoken_at_home = models.ManyToManyField(
        Language,
        verbose_name=_("languages spoken at home"),
        related_name="children",
        blank=True,
    )

    objects = ChildQuerySet.as_manager()

    class Meta:
        verbose_name = _("child")
        verbose_name_plural = _("children")
        ordering = ["birthyear", "name"]

    def __str__(self):
        return f"{self.name} ({self.birthyear})"

    @transaction.atomic()
    def delete(self, *args, **kwargs):
        self.enrolments.upcoming().delete()
        return super().delete(*args, **kwargs)

    def can_user_administer(self, user):
        return user.can_administer_project(self.project)

    def get_enrolment_count(self, year: Optional[int] = None, past=False):
        from events.models import Event  # noqa

        if year and past:
            raise ValueError("Cannot use year and past arguments at the same time.")
        now = timezone.now()
        year = year or now.year

        occurrence_filters = Q(time__year=year)
        # For external ticket system events published_at field is used to determine the
        # event's year. That is obviously not a perfect solution, but the best we can
        # do with the current data, and most probably good enough.
        ticket_system_filters = Q(event__published_at__year=year)
        if past:
            occurrence_filters &= Q(time__lt=now)
            ticket_system_filters &= Q(event__published_at__lt=now)
        return (
            self.occurrences.filter(occurrence_filters).count()
            + self.ticket_system_passwords.filter(ticket_system_filters)
            .distinct()
            .count()
        )

    @staticmethod
    def _hash(values: Iterable[str]) -> str:
        return sha256(",".join(values).encode("utf8")).hexdigest()

    @property
    def _salt_birthyear_postal_code_guardian_emails_list(self) -> list[str]:
        """
        List of salt, child's birthyear, postal code and guardians' emails.
        """
        return [
            settings.KUKKUU_HASHID_SALT,
            self.birthyear.isoformat(),
            self.postal_code,
            *sorted(guardian.email for guardian in self.guardians.all()),
        ]

    @property
    def birthyear_postal_code_guardian_emails_hash(self) -> str:
        """
        Salted hash of child's birthyear, postal code and guardians' emails.
        """
        return self._hash(self._salt_birthyear_postal_code_guardian_emails_list)

    @property
    def name_birthyear_postal_code_guardian_emails_hash(self) -> str:
        """
        Salted hash of child's name, birthyear, postal
        code and guardians' emails.
        """
        return self._hash(
            [self.name] + self._salt_birthyear_postal_code_guardian_emails_list
        )


class RelationshipQuerySet(models.QuerySet):
    def user_can_view(self, user):
        return self.filter(
            Q(guardian__user=user) | Q(child__project__in=user.administered_projects)
        ).distinct()


class Relationship(models.Model):
    PARENT = "parent"  # In Finnish: Vanhempi
    OTHER_GUARDIAN = "other_guardian"  # In Finnish: Muu huoltaja
    OTHER_RELATION = "other_relation"  # In Finnish: Muu läheinen
    ADVOCATE = "advocate"  # In Finnish: Virallinen puolesta-asioija
    TYPE_CHOICES = (
        (PARENT, _("Parent")),
        (OTHER_GUARDIAN, _("Other guardian")),
        (OTHER_RELATION, _("Other relation")),
        (ADVOCATE, _("Advocate")),
    )

    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    child = models.ForeignKey(
        Child,
        verbose_name=_("child"),
        related_name="relationships",
        on_delete=models.CASCADE,
    )
    guardian = models.ForeignKey(
        Guardian,
        verbose_name=_("guardian"),
        on_delete=models.CASCADE,
        related_name="relationships",
    )
    type = models.CharField(
        verbose_name=_("type"),
        choices=TYPE_CHOICES,
        max_length=64,
        null=True,
        blank=True,
    )

    objects = RelationshipQuerySet.as_manager()

    class Meta:
        verbose_name = _("relationship")
        verbose_name_plural = _("relationships")
        ordering = [
            "guardian",
            "child",
        ]
