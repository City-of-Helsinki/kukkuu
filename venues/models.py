from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatedFields

from common.models import TimestampedModel, TranslatableModel


class Venue(TimestampedModel, TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255),
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
        www_url=models.URLField(verbose_name=_("url"), blank=True),
    )

    class Meta:
        verbose_name = _("venue")
        verbose_name_plural = _("venues")

    def __str__(self):
        return self.safe_translation_getter("name", super().__str__())
