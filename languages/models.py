from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ExpressionWrapper, Q
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatedFields

from common.models import TranslatableModel, TranslatableQuerySet

from .consts import (
    OTHER_LANGUAGE_ALPHA_3_CODE,
    SPECIAL_LANGUAGE_ALPHA_3_CODES,
    SPEECHLESS_LANGUAGE_ALPHA_3_CODE,
)
from .exceptions import InvalidLanguageCodeError


class LanguageQueryset(TranslatableQuerySet):
    def get_option_other(self):
        return self.get(alpha_3_code=OTHER_LANGUAGE_ALPHA_3_CODE)

    def get_option_speechless(self):
        return self.get(alpha_3_code=SPEECHLESS_LANGUAGE_ALPHA_3_CODE)

    def with_is_special_language(self):
        """
        Annotate the queryset with a boolean field `is_special_language`
        that is True for all ISO 639-3 special type languages i.e. for:
         - "mis" (Uncoded languages)
         - "mul" (Multiple languages)
         - "und" (Undetermined) i.e. "Other language"
         - "zxx" (No linguistic content) i.e. "Speechless"
        and otherwise False.

        See https://iso639-3.sil.org/code_tables/639/data
        """
        return self.annotate(
            is_special_language=ExpressionWrapper(
                Q(alpha_3_code__in=SPECIAL_LANGUAGE_ALPHA_3_CODES),
                output_field=models.BooleanField(),
            )
        )


class Language(TranslatableModel):
    """
    A language identified by its ISO 639-3 alpha-3 code.

    The flags `can_be_spoken_at_home` and `can_be_occurrence_language` tell where the
    language may be used. They are enforced when a language is chosen, so changing
    a flag does not remove existing links to the language.
    """

    alpha_3_code = models.CharField(
        max_length=3,
        verbose_name=_("alpha-3 code"),
        help_text=_("ISO 639-3 alpha-3 code"),
        unique=True,
    )
    can_be_spoken_at_home = models.BooleanField(
        default=True,
        verbose_name=_("can be spoken at home"),
        help_text=_(
            "Whether this language can be chosen as a language spoken at home."
        ),
    )
    can_be_occurrence_language = models.BooleanField(
        default=True,
        verbose_name=_("can be occurrence language"),
        help_text=_(
            "Whether this language can be chosen as an occurrence language "
            "and be used for filtering occurrences."
        ),
    )
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("name"), max_length=255, blank=True),
    )

    objects = LanguageQueryset.as_manager()

    class Meta:
        verbose_name = _("language")
        verbose_name_plural = _("languages")

    def __str__(self):
        return f"{self.name} ({self.alpha_3_code})"

    def clean(self):
        from .services import LanguageService

        try:
            LanguageService.get_pycountry_language(self.alpha_3_code)
        except InvalidLanguageCodeError as e:
            raise ValidationError({"alpha_3_code": e})
