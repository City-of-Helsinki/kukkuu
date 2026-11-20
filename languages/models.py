import gettext

import pycountry
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
)


class InvalidLanguageCodeError(Exception):
    pass


class LanguageAlreadyExistsError(Exception):
    pass


class LanguageQueryset(TranslatableQuerySet):
    @transaction.atomic
    def create_from_language_code(self, language_code):
        pycountry_language = get_pycountry_language(language_code)

        with translation.override("en"):
            try:
                obj = self.create(
                    alpha_3_code=pycountry_language.alpha_3,
                    name=pycountry_language.name,
                )
            except IntegrityError as e:
                raise LanguageAlreadyExistsError(e)

        for parler_language in PARLER_SUPPORTED_LANGUAGE_CODES:
            if parler_language == "en":
                continue

            gettext_translation = gettext.translation(
                "iso639-3", pycountry.LOCALES_DIR, languages=[parler_language]
            )
            obj.create_translation(
                parler_language,
                name=gettext_translation.gettext(pycountry_language.name),
            )

        return obj

    def create_option_other(self):
        try:
            return self.create_translatable_object(
                alpha_3_code=OTHER_LANGUAGE_ALPHA_3_CODE,
                translations=[
                    {"language_code": language_code, "name": name}
                    for language_code, name in OTHER_LANGUAGE_NAMES.items()
                ],
            )
        except IntegrityError as e:
            raise LanguageAlreadyExistsError(e)

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
        help_text=_("ISO 639-3 (language) or ISO 639-5 (language family) alpha-3 code"),
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
    language = pycountry.languages.get(
        alpha_3=language_code
    ) or pycountry.language_families.get(alpha_3=language_code)

    if not language:
        raise InvalidLanguageCodeError(f'Invalid language code "{language_code}"')

    return language
