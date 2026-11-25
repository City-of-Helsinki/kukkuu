from dataclasses import astuple, dataclass
from functools import cache

import pycountry

from .enums import LanguageType
from .services import LanguageService


@dataclass(frozen=True)
class LivingLanguage:
    alpha_3: str
    name_fi: str
    name_sv: str
    name_en: str


@cache
def get_living_languages() -> tuple[LivingLanguage, ...]:
    """
    Get the living ISO 639-3 languages, ordered by their alpha-3 codes. The English
    name is used where Unicode CLDR has no Finnish or Swedish name.
    """
    get_cldr_language_name = LanguageService.get_cldr_language_name
    return tuple(
        sorted(
            (
                LivingLanguage(
                    alpha_3=language.alpha_3,
                    name_fi=get_cldr_language_name(language, "fi") or language.name,
                    name_sv=get_cldr_language_name(language, "sv") or language.name,
                    name_en=language.name,
                )
                for language in pycountry.languages
                if language.type == LanguageType.LIVING.value
            ),
            key=lambda language: language.alpha_3,
        )
    )


def search_living_languages(search_term):
    """
    Get the living ISO 639-3 languages whose alpha-3 code or Finnish, Swedish or
    English name contains the search term, ignoring case.
    """
    search_term = search_term.strip().casefold()
    return [
        language
        for language in get_living_languages()
        if any(search_term in value.casefold() for value in astuple(language))
    ]
