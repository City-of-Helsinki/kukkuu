from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from helsinki_gdpr.models import SerializableMixin
from parler.models import TranslatedFields

from common.models import TimestampedModel, TranslatableModel, TranslatableQuerySet
from common.utils import get_translations_dict


class VenueQuerySet(TranslatableQuerySet):
    def delete(self):
        if self.filter(is_system=True).exists():
            raise ValidationError(_("The system venue cannot be deleted."))
        return super().delete()


class Venue(TimestampedModel, TranslatableModel, SerializableMixin):
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255, blank=True),
        description=models.TextField(verbose_name=_("description"), blank=True),
        address=models.CharField(
            verbose_name=_("address"), max_length=1000, blank=True
        ),
        accessibility_info=models.TextField(
            verbose_name=_("accessibility info"), blank=True
        ),
        arrival_instructions=models.TextField(
            verbose_name=_("arrival instructions"), blank=True
        ),
        additional_info=models.TextField(verbose_name=_("additional info"), blank=True),
        wc_and_facilities=models.TextField(
            verbose_name=_("WC & facilities"), blank=True
        ),
        www_url=models.URLField(verbose_name=_("url"), blank=True),
    )
    is_system = models.BooleanField(
        verbose_name=_("is system"),
        default=False,
    )
    project = models.ForeignKey(
        "projects.Project",
        verbose_name=_("project"),
        related_name="venues",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    objects = VenueQuerySet.as_manager()

    serialize_fields = [
        {"name": "name_with_translations"},
        {"name": "address_with_translations"},
    ]

    class Meta:
        verbose_name = _("venue")
        verbose_name_plural = _("venues")
        constraints = [
            models.UniqueConstraint(
                fields=["is_system"],
                condition=models.Q(is_system=True),
                name="unique_system_venue",
            ),
            models.CheckConstraint(
                condition=(
                    (models.Q(is_system=True) & models.Q(project__isnull=True))
                    | (models.Q(is_system=False) & models.Q(project__isnull=False))
                ),
                name="system_venue_has_no_project_check",
            ),
        ]

    @property
    def name_with_translations(self):
        return get_translations_dict(self, "name")

    @property
    def address_with_translations(self):
        return get_translations_dict(self, "address")

    def __str__(self):
        name = self.safe_translation_getter("name", super().__str__())
        if self.project:
            return f"{name} ({self.pk}) ({self.project.year})"
        return f"{name} ({self.pk})"

    def can_user_administer(self, user):
        if not user or not user.is_authenticated:
            return False
        if self.is_system:
            return user.is_system_administrator
        return user.can_administer_project(self.project) if self.project else False

    def clean(self):
        super().clean()
        if self.is_system:
            if self.project is not None:
                raise ValidationError(_("System venue cannot belong to a project."))
            existing = Venue.objects.filter(is_system=True)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(_("There can be only one system venue."))
        elif self.project is None:
            raise ValidationError(_("Regular venue must belong to a project."))

        if self.pk and not self._state.adding:
            original = Venue.objects.filter(pk=self.pk).values("is_system").first()
            if original and original["is_system"] and not self.is_system:
                raise ValidationError(_("The system venue flag cannot be cleared."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_system:
            raise ValidationError(_("The system venue cannot be deleted."))
        return super().delete(*args, **kwargs)
