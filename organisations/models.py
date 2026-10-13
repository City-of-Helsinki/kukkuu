from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from helsinki_gdpr.models import SerializableMixin

from common.models import TimestampedModel, UUIDPrimaryKeyModel


class OrganisationQuerySet(models.QuerySet):
    def user_can_view(self, user):
        if not user.is_authenticated:
            return self.none()
        if user.is_system_administrator:
            return self.all()
        # Returns only the organisations where this user is a member
        # (uses Django's M2M reverse relationship filtering)
        return self.filter(users=user).distinct()

    def delete(self):
        if self.filter(is_system=True).exists():
            raise ValidationError(_("The system organisation cannot be deleted."))
        return super().delete()


class Organisation(TimestampedModel, UUIDPrimaryKeyModel, SerializableMixin):
    name = models.CharField(verbose_name=_("name"), max_length=255, unique=True)
    is_system = models.BooleanField(
        verbose_name=_("is system"),
        default=False,
    )

    objects = OrganisationQuerySet.as_manager()

    serialize_fields = (
        {"name": "id", "accessor": lambda uuid: str(uuid)},
        {"name": "name"},
    )

    class Meta:
        verbose_name = _("organisation")
        verbose_name_plural = _("organisations")
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_system"],
                condition=models.Q(is_system=True),
                name="unique_system_organisation",
            )
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.is_system:
            existing = Organisation.objects.filter(is_system=True)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(_("There can be only one system organisation."))
        if self.pk and not self._state.adding:
            original = (
                Organisation.objects.filter(pk=self.pk).values("is_system").first()
            )
            if original and original["is_system"] and not self.is_system:
                raise ValidationError(
                    _("The system organisation flag cannot be cleared.")
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_system:
            raise ValidationError(_("The system organisation cannot be deleted."))
        return super().delete(*args, **kwargs)
