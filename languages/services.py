from dataclasses import dataclass

import pycountry
from babel import Locale
from django.db import IntegrityError, transaction
from django.utils import translation

from kukkuu.settings import PARLER_SUPPORTED_LANGUAGE_CODES

from .consts import (
    OTHER_LANGUAGE_ALPHA_3_CODE,
    OTHER_LANGUAGE_NAMES,
    SPEECHLESS_LANGUAGE_ALPHA_3_CODE,
    SPEECHLESS_LANGUAGE_NAMES,
)
from .exceptions import (
    InvalidLanguageCodeError,
    LanguageAlreadyExistsError,
    LanguageNameNotFoundError,
)
from .models import Language


@dataclass(frozen=True)
class CreatedLanguage:
    """
    A created language.

    Attributes:
        language: The created Language object.
        fallback_language_codes: Codes of the languages in which the name of the
            created language is the English name, because CLDR has no name in them.
    """

    language: Language
    fallback_language_codes: tuple[str, ...] = ()


class LanguageService:
    """
    Service class for creating languages and getting the names of ISO 639-3 languages.
    """

    @staticmethod
    def get_pycountry_language(language_code):
        language = pycountry.languages.get(alpha_3=language_code)

        if not language:
            raise InvalidLanguageCodeError(f'Invalid language code "{language_code}"')

        return language

    @staticmethod
    def get_cldr_language_name(pycountry_language, parler_language):
        """
        Get the name of the language in the given language from Unicode CLDR, or None
        if CLDR has no such name.

        CLDR identifies languages with BCP 47 language subtags, which are the shortest
        ISO 639 codes: the alpha-2 code if the language has one, else the alpha-3 code.

        Links:
        - https://www.rfc-editor.org/rfc/rfc5646#section-2.1
          (BCP 47 language tag syntax: the language subtag is the "shortest ISO 639
          code")
        - https://unicode.org/reports/tr35/tr35.html#Unicode_language_identifier
          (CLDR's language subtags are based on the BCP 47 language subtags)
        - https://babel.pocoo.org/en/latest/api/core.html#babel.core.Locale.languages
          (Babel's mapping from language subtags to the CLDR names)
        """
        names = Locale(parler_language).languages
        alpha_2 = getattr(pycountry_language, "alpha_2", None)
        return names.get(alpha_2) or names.get(pycountry_language.alpha_3)

    @classmethod
    @transaction.atomic
    def create_from_language_code(
        cls, language_code, use_english_fallback=False
    ) -> CreatedLanguage:
        """
        Create a language from an ISO 639-3 code.

        The English name is from pycountry and the other names are from Unicode CLDR.
        If CLDR has no name for the language in some supported language, raise
        LanguageNameNotFoundError, or with use_english_fallback use the English name
        for the missing names.
        """
        pycountry_lang = cls.get_pycountry_language(language_code)

        names = {
            parler_lang: cls.get_cldr_language_name(pycountry_lang, parler_lang)
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
                obj = Language.objects.create(
                    alpha_3_code=pycountry_lang.alpha_3,
                    name=pycountry_lang.name,
                )
            except IntegrityError as e:
                raise LanguageAlreadyExistsError(e)

        for parler_lang, name in names.items():
            obj.create_translation(parler_lang, name=name)

        return CreatedLanguage(language=obj, fallback_language_codes=tuple(missing))

    @staticmethod
    def _create_special_language(
        *,
        alpha_3_code,
        names,
        can_be_spoken_at_home,
        can_be_occurrence_language,
    ):
        try:
            return Language.objects.create_translatable_object(
                alpha_3_code=alpha_3_code,
                can_be_spoken_at_home=can_be_spoken_at_home,
                can_be_occurrence_language=can_be_occurrence_language,
                translations=[
                    {"language_code": language_code, "name": name}
                    for language_code, name in names.items()
                ],
            )
        except IntegrityError as e:
            raise LanguageAlreadyExistsError(e)

    @classmethod
    def create_option_other(cls):
        """
        Create the "Other" language, which can't be used as an occurrence language.
        """
        return cls._create_special_language(
            alpha_3_code=OTHER_LANGUAGE_ALPHA_3_CODE,
            names=OTHER_LANGUAGE_NAMES,
            can_be_spoken_at_home=True,
            can_be_occurrence_language=False,
        )

    @classmethod
    def create_option_speechless(cls):
        """
        Create the "Speechless" language, which can't be used as a language spoken
        at home.
        """
        return cls._create_special_language(
            alpha_3_code=SPEECHLESS_LANGUAGE_ALPHA_3_CODE,
            names=SPEECHLESS_LANGUAGE_NAMES,
            can_be_spoken_at_home=False,
            can_be_occurrence_language=True,
        )
