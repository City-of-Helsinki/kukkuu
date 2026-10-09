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


class Organisation(TimestampedModel, UUIDPrimaryKeyModel, SerializableMixin):
    name = models.CharField(verbose_name=_("name"), max_length=255, unique=True)

    objects = OrganisationQuerySet.as_manager()

    serialize_fields = (
        {"name": "id", "accessor": lambda uuid: str(uuid)},
        {"name": "name"},
    )

    class Meta:
        verbose_name = _("organisation")
        verbose_name_plural = _("organisations")
        ordering = ["name"]

    def __str__(self):
        return self.name
