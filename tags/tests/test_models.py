import pytest

from tags.factories import ThemePathFactory
from tags.models import ThemePath

TEST_TRANSLATIONS = {
    "fi": {"name": "Nimi", "description": "Kuvaus"},
    "sv": {"name": "Namn", "description": "Beskrivning"},
    "en": {"name": "Name", "description": "Description"},
}

EMPTY_TRANSLATIONS = {
    "fi": {"name": None, "description": None},
    "sv": {"name": None, "description": None},
    "en": {"name": None, "description": None},
}


def _add_translations_to_tag(tag):
    for language_code, fields in TEST_TRANSLATIONS.items():
        tag.create_translation(language_code, **fields)


def _get_translations(tag):
    return {
        language_code: {
            field: tag.safe_translation_getter(field, language_code=language_code)
            for field in fields
        }
        for language_code, fields in TEST_TRANSLATIONS.items()
    }


@pytest.mark.django_db
def test_theme_paths_are_ordered_by_sort_order_then_slug():
    """Test that ThemePath objects are ordered by (sort_order, slug)"""
    ThemePathFactory(sort_order=None, slug="test_unordered")
    ThemePathFactory(sort_order=2, slug="test_2_b")
    ThemePathFactory(sort_order=1, slug="test_first")
    ThemePathFactory(sort_order=2, slug="test_2_a")

    slugs = ThemePath.objects.filter(slug__startswith="test_").values_list(
        "slug", flat=True
    )

    assert list(slugs) == ["test_first", "test_2_a", "test_2_b", "test_unordered"]


@pytest.mark.django_db
def test_theme_path_translations():
    """Test that ThemePath's translations of `name` and `description` work."""
    theme_path = ThemePath.objects.create(slug="translated")
    assert (
        _get_translations(ThemePath.objects.get(pk="translated")) == EMPTY_TRANSLATIONS
    )
    _add_translations_to_tag(theme_path)

    assert _get_translations(ThemePath.objects.get(pk="translated")) == (
        TEST_TRANSLATIONS
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("translated_languages", "current_language", "expected_str"),
    [
        (["fi", "sv", "en"], "en", "name_en"),
        (["fi", "en"], "sv", "name_fi"),
        (["sv", "en"], "fi", "name_sv"),
        (["en"], "sv", "name_en"),
        ([], "fi", "str_slug"),
    ],
)
def test_theme_path_str_uses_current_language_then_fi_sv_en_then_slug(
    translated_languages, current_language, expected_str
):
    theme_path = ThemePath.objects.create(slug="str_slug")
    for language_code in translated_languages:
        theme_path.create_translation(language_code, name=f"name_{language_code}")
    theme_path.set_current_language(current_language)

    assert str(theme_path) == expected_str


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("descriptions", "current_language", "expected_description"),
    [
        ({"fi": "kuvaus_fi", "sv": "beskrivning_sv"}, "sv", "beskrivning_sv"),
        ({"fi": "kuvaus_fi", "sv": ""}, "sv", "kuvaus_fi"),
        ({"sv": "beskrivning_sv", "en": "description_en"}, "fi", "beskrivning_sv"),
        ({}, "fi", ""),
    ],
)
def test_theme_path_get_translated_value_falls_back_for_description(
    descriptions, current_language, expected_description
):
    theme_path = ThemePath.objects.create(slug="description_slug")
    for language_code, description in descriptions.items():
        theme_path.create_translation(
            language_code, name="name", description=description
        )
    theme_path.set_current_language(current_language)

    assert (
        theme_path.get_translated_value("description", default="")
        == expected_description
    )
