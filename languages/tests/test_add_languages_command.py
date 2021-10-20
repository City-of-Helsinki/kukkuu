from io import StringIO

import pytest
from django.core.management import call_command

from kukkuu.settings import PARLER_SUPPORTED_LANGUAGE_CODES
from languages.models import Language


def call_command_and_assert_output(snapshot, *args, **kwargs):
    with StringIO() as out:
        call_command("add_languages", *args, **kwargs, stdout=out)
        snapshot.assert_match(out.getvalue())


def get_serialized_languages():
    ret = {}
    for language in Language.objects.all():
        name = {
            parler_language: language.safe_translation_getter(
                "name", language_code=parler_language
            )
            for parler_language in PARLER_SUPPORTED_LANGUAGE_CODES
        }
        ret[language.alpha_3_code] = name

    return ret


@pytest.fixture
def initial_language():
    return Language.objects.create(alpha_3_code="fin", name="INITIAL Finnish")


@pytest.mark.django_db
def test_no_arguments(snapshot):
    call_command_and_assert_output(snapshot)


@pytest.mark.django_db
def test_add_default_languages(snapshot):
    call_command_and_assert_output(snapshot, "--default")
    snapshot.assert_match(get_serialized_languages())


@pytest.mark.django_db
def test_add_languages(snapshot):
    call_command_and_assert_output(snapshot, "abd,agh")
    snapshot.assert_match(get_serialized_languages())


@pytest.mark.django_db
def test_add_languages_and_flush(snapshot, initial_language):
    call_command_and_assert_output(snapshot, "abd,agh", "--flush")
    snapshot.assert_match(get_serialized_languages())
