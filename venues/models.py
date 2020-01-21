from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatedFields

from common.models import TimestampedModel, TranslatableModel


class Venue(TimestampedModel, TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255),
        description=models.TextField(verbose_name=_("description"), blank=True),
    )
    seat_count = models.PositiveIntegerField(verbose_name=_("seat count"))

    class Meta:
        verbose_name = _("venue")
        verbose_name_plural = _("venues")

    def __str__(self):
        return f"{self.pk} {self.name}"
