import pytest

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
def test_tags_are_ordered_by_sort_order_then_slug(tag_model):
    """Test that tags are ordered by (sort_order, slug)"""
    tag_model.objects.create(sort_order=None, slug="test_unordered")
    tag_model.objects.create(sort_order=2, slug="test_2_b")
    tag_model.objects.create(sort_order=1, slug="test_first")
    tag_model.objects.create(sort_order=2, slug="test_2_a")

    slugs = tag_model.objects.filter(slug__startswith="test_").values_list(
        "slug", flat=True
    )

    assert list(slugs) == ["test_first", "test_2_a", "test_2_b", "test_unordered"]


@pytest.mark.django_db
def test_tag_translations(tag_model):
    """Test that a tag's translations of `name` and `description` work."""
    tag = tag_model.objects.create(slug="translated")
    assert _get_translations(tag_model.objects.get(pk="translated")) == (
        EMPTY_TRANSLATIONS
    )
    _add_translations_to_tag(tag)

    assert _get_translations(tag_model.objects.get(pk="translated")) == (
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
def test_tag_str_uses_current_language_then_fi_sv_en_then_slug(
    tag_model, translated_languages, current_language, expected_str
):
    tag = tag_model.objects.create(slug="str_slug")
    for language_code in translated_languages:
        tag.create_translation(language_code, name=f"name_{language_code}")
    tag.set_current_language(current_language)

    assert str(tag) == expected_str


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
def test_tag_get_translated_value_falls_back_for_description(
    tag_model, descriptions, current_language, expected_description
):
    tag = tag_model.objects.create(slug="description_slug")
    for language_code, description in descriptions.items():
        tag.create_translation(language_code, name="name", description=description)
    tag.set_current_language(current_language)

    assert tag.get_translated_value("description", default="") == expected_description
