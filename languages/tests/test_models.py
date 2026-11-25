import pytest
from django.core.exceptions import ValidationError

from languages.exceptions import LanguageAlreadyExistsError
from languages.models import Language


@pytest.mark.parametrize("alpha_3_code", ["sme", "und"])
def test_language_clean_accepts_iso_639_3_codes(alpha_3_code):
    Language(alpha_3_code=alpha_3_code).clean()


def test_language_clean_rejects_iso_639_5_codes():
    with pytest.raises(ValidationError):
        Language(alpha_3_code="smi").clean()


@pytest.mark.django_db
def test_create_option_speechless():
    Language.objects.all().delete()

    language = Language.objects.create_option_speechless()

    assert language.alpha_3_code == "zxx"
    assert Language.objects.get_option_speechless() == language
    assert not language.can_be_spoken_at_home
    assert language.can_be_occurrence_language
    assert {t.language_code: t.name for t in language.translations.all()} == {
        "fi": "Sanaton",
        "sv": "Ordlös",
        "en": "Speechless",
    }
    with pytest.raises(LanguageAlreadyExistsError):
        Language.objects.create_option_speechless()


@pytest.mark.django_db
def test_create_option_other():
    Language.objects.all().delete()

    language = Language.objects.create_option_other()

    assert language.alpha_3_code == "und"
    assert Language.objects.get_option_other() == language
    assert language.can_be_spoken_at_home
    assert not language.can_be_occurrence_language
