import gettext

import pycountry
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from common.models import TranslatableQuerySet
from kukkuu.settings import PARLER_SUPPORTED_LANGUAGE_CODES


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

    @transaction.atomic
    def create_option_other(self):
        obj, created = self.language("en").get_or_create(
            alpha_3_code=None,
            translations__name="Other language",
            defaults={"name": "Other language"},
        )
        if not created:
            raise LanguageAlreadyExistsError()

        obj.create_translation("sv", name="Annat språk")
        obj.create_translation("fi", name="muu kieli")

        return obj


class Language(TranslatableModel):
    alpha_3_code = models.CharField(
        max_length=3,
        verbose_name=_("alpha-3 code"),
        help_text=_("ISO 639-3 (language) or ISO 639-5 (language family) alpha-3 code"),
        unique=True,
        null=True,
        blank=True,
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
        if self.alpha_3_code:
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
