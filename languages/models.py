from dataclasses import dataclass

import pycountry
from babel import Locale
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.db.models import ExpressionWrapper, Q
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatedFields

from common.models import TranslatableModel, TranslatableQuerySet
from kukkuu.settings import PARLER_SUPPORTED_LANGUAGE_CODES

from .consts import (
    OTHER_LANGUAGE_ALPHA_3_CODE,
    OTHER_LANGUAGE_NAMES,
    SPECIAL_LANGUAGE_ALPHA_3_CODES,
    SPEECHLESS_LANGUAGE_ALPHA_3_CODE,
    SPEECHLESS_LANGUAGE_NAMES,
)


class InvalidLanguageCodeError(Exception):
    pass


class LanguageNameNotFoundError(Exception):
    pass


class LanguageAlreadyExistsError(Exception):
    pass


@dataclass(frozen=True)
class CreatedLanguage:
    """
    A created language.

    Attributes:
        language: The created Language object.
        fallback_language_codes: Codes of the languages in which the name of the
            created language is the English name, because CLDR has no name in them.
    """

    language: "Language"
    fallback_language_codes: tuple[str, ...] = ()


class LanguageQueryset(TranslatableQuerySet):
    @transaction.atomic
    def create_from_language_code(
        self, language_code, use_english_fallback=False
    ) -> CreatedLanguage:
        """
        Create a language from an ISO 639-3 code.

        The English name is from pycountry and the other names are from Unicode CLDR.
        If CLDR has no name for the language in some supported language, raise
        LanguageNameNotFoundError, or with use_english_fallback use the English name
        for the missing names.
        """
        pycountry_lang = get_pycountry_language(language_code)

        names = {
            parler_lang: get_cldr_language_name(pycountry_lang, parler_lang)
            for parler_lang in PARLER_SUPPORTED_LANGUAGE_CODES
            if parler_lang != "en"
        }
        missing = [lang for lang, name in names.items() if not name]
        if missing and not use_english_fallback:
            raise LanguageNameNotFoundError(
                f'No CLDR name for language "{language_code}" '
                f"in language(s): {', '.join(missing)}"
            )
        for lang in missing:
            names[lang] = pycountry_lang.name

        with translation.override("en"):
            try:
                obj = self.create(
                    alpha_3_code=pycountry_lang.alpha_3,
                    name=pycountry_lang.name,
                )
            except IntegrityError as e:
                raise LanguageAlreadyExistsError(e)

        for parler_lang, name in names.items():
            obj.create_translation(parler_lang, name=name)

        return CreatedLanguage(language=obj, fallback_language_codes=tuple(missing))

    def _create_special_language(self, alpha_3_code, names):
        try:
            return self.create_translatable_object(
                alpha_3_code=alpha_3_code,
                translations=[
                    {"language_code": language_code, "name": name}
                    for language_code, name in names.items()
                ],
            )
        except IntegrityError as e:
            raise LanguageAlreadyExistsError(e)

    def create_option_other(self):
        return self._create_special_language(
            OTHER_LANGUAGE_ALPHA_3_CODE, OTHER_LANGUAGE_NAMES
        )

    def create_option_speechless(self):
        return self._create_special_language(
            SPEECHLESS_LANGUAGE_ALPHA_3_CODE, SPEECHLESS_LANGUAGE_NAMES
        )

    def with_is_special(self):
        return self.annotate(
            is_special=ExpressionWrapper(
                Q(alpha_3_code__in=SPECIAL_LANGUAGE_ALPHA_3_CODES),
                output_field=models.BooleanField(),
            )
        )


class Language(TranslatableModel):
    alpha_3_code = models.CharField(
        max_length=3,
        verbose_name=_("alpha-3 code"),
        help_text=_("ISO 639-3 alpha-3 code"),
        unique=True,
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
        try:
            get_pycountry_language(self.alpha_3_code)
        except InvalidLanguageCodeError as e:
            raise ValidationError({"alpha_3_code": e})


def get_pycountry_language(language_code):
    language = pycountry.languages.get(alpha_3=language_code)

    if not language:
        raise InvalidLanguageCodeError(f'Invalid language code "{language_code}"')

    return language


def get_cldr_language_name(pycountry_language, parler_language):
    """
    Get the name of the language in the given language from Unicode CLDR, or None if
    CLDR has no such name.

    CLDR identifies languages with BCP 47 language subtags, which are the shortest
    ISO 639 codes: the alpha-2 code if the language has one, else the alpha-3 code.

    Links:
    - https://www.rfc-editor.org/rfc/rfc5646#section-2.1
      (BCP 47 language tag syntax: the language subtag is the "shortest ISO 639 code")
    - https://unicode.org/reports/tr35/tr35.html#Unicode_language_identifier
      (CLDR's language subtags are based on the BCP 47 language subtags)
    - https://babel.pocoo.org/en/latest/api/core.html#babel.core.Locale.languages
      (Babel's mapping from language subtags to the CLDR names)
    """
    names = Locale(parler_language).languages
    alpha_2 = getattr(pycountry_language, "alpha_2", None)
    return names.get(alpha_2) or names.get(pycountry_language.alpha_3)
