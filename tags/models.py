from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatedFields

from common.models import TimestampedModel, TranslatableModel


class Tag(TimestampedModel, TranslatableModel):
    """Abstract base of the tag models.

    Each concrete tag model has its own table and declares its own `translations`,
    because django-parler can't create a translations model for an abstract model.
    """

    slug = models.SlugField(
        verbose_name=_("slug"),
        help_text=_(
            "Stable identifier of the tag. Use lowercase letters and underscores."
        ),
        primary_key=True,
    )
    sort_order = models.PositiveIntegerField(
        verbose_name=_("sort order"),
        help_text=_("Tags without a sort order are listed last."),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
        ordering = ["sort_order", "slug"]

    def get_translated_value(self, field_name, *, default):
        language_codes = [
            self.get_current_language(),
            *settings.PARLER_SUPPORTED_LANGUAGE_CODES,
        ]
        values = (
            self.safe_translation_getter(field_name, language_code=language_code)
            for language_code in language_codes
        )
        return next((value for value in values if value), default)

    def __str__(self):
        return self.get_translated_value("name", default=self.slug)


class ThemePath(Tag):
    """Theme path (Finnish: "teemapolku")."""

    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255),
        description=models.TextField(verbose_name=_("description"), blank=True),
    )

    class Meta(Tag.Meta):
        verbose_name = _("theme path")
        verbose_name_plural = _("theme paths")
