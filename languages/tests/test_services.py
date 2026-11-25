import pytest

from languages.exceptions import LanguageAlreadyExistsError
from languages.models import Language
from languages.services import LanguageService


@pytest.mark.django_db
def test_create_option_speechless():
    Language.objects.all().delete()

    language = LanguageService.create_option_speechless()

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
        LanguageService.create_option_speechless()


@pytest.mark.django_db
def test_create_option_other():
    Language.objects.all().delete()

    language = LanguageService.create_option_other()

    assert language.alpha_3_code == "und"
    assert Language.objects.get_option_other() == language
    assert language.can_be_spoken_at_home
    assert not language.can_be_occurrence_language
