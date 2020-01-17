from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatedFields

from common.models import TimestampedModel, TranslatableModel
from venues.models import Venue


class Event(TimestampedModel, TranslatableModel):
    CHILD_AND_GUARDIAN = "child_and_guardian"
    FAMILY = "family"
    PARTICIPANT_AMOUNT_CHOICES = (
        (CHILD_AND_GUARDIAN, _("Child and Guardian")),
        (FAMILY, _("Family")),
    )

    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255),
        short_description=models.TextField(
            verbose_name=_("short description"), blank=True
        ),
        description=models.TextField(verbose_name=_("description"), blank=True),
    )
    image = models.ImageField(blank=True, verbose_name=_("image"))
    participants_per_invite = models.CharField(
        max_length=255,
        choices=PARTICIPANT_AMOUNT_CHOICES,
        verbose_name=_("participants per invite"),
    )
    duration = models.PositiveSmallIntegerField(
        verbose_name=_("duration"), blank=True, null=True, help_text=_("In minutes")
    )
    capacity_per_occurrence = models.PositiveSmallIntegerField(
        verbose_name=_("capacity per occurrence")
    )
    published_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("published at")
    )

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")

    def __str__(self):
        return self.safe_translation_getter("name", super().__str__())


class Occurrence(TimestampedModel):
    time = models.DateTimeField(verbose_name=_("time"))
    event = models.ForeignKey(
        Event,
        verbose_name=_("event"),
        related_name="occurrences",
        on_delete=models.CASCADE,
    )
    venue = models.ForeignKey(
        Venue,
        verbose_name=_("venue"),
        related_name="occurrences",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("occurrence")
        verbose_name_plural = _("occurrences")

    def __str__(self):
        return f"{self.pk} {self.time}"
