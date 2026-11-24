import pytest
from django.urls import reverse

from languages.models import Language
from users.factories import GuardianFactory

CHANGELIST_URL_NAME = "admin:languages_language_changelist"
ADD_LIVING_URL_NAME = "admin:languages_language_add_living"


def _search(client, term, **params):
    response = client.get(reverse(ADD_LIVING_URL_NAME), {"search_term": term, **params})
    assert response.status_code == 200
    return response


def _messages(response):
    return [str(message) for message in response.context["messages"]]


@pytest.mark.django_db
def test_language_changelist_links_to_add_living_language_page(admin_client, languages):
    response = admin_client.get(reverse(CHANGELIST_URL_NAME))

    assert response.status_code == 200
    assert reverse(ADD_LIVING_URL_NAME) in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("term", "expected_codes"),
    [
        ("fin", {"fin"}),
        ("FIN", {"fin"}),
        ("suomi", {"fin"}),
        ("finska", {"fin"}),
        ("Finnish", {"fin"}),
        ("swe", {"swe"}),
        ("ruotsi", {"swe"}),
        ("svenska", {"swe"}),
        ("ish", {"eng", "fin", "swe"}),
    ],
)
def test_language_changelist_search_returns_only_languages_matching_the_term(
    admin_client, languages, term, expected_codes
):
    response = admin_client.get(reverse(CHANGELIST_URL_NAME), {"q": term})

    codes = {language.alpha_3_code for language in response.context["cl"].result_list}
    assert codes == expected_codes


@pytest.mark.django_db
def test_language_changelist_search_does_not_multiply_guardian_count(
    admin_client, languages
):
    GuardianFactory.create_batch(2, languages_spoken_at_home=["fin"])

    response = admin_client.get(reverse(CHANGELIST_URL_NAME), {"q": "fin"})

    result_list = response.context["cl"].result_list
    assert [
        (language.alpha_3_code, language.guardians__count) for language in result_list
    ] == [("fin", 2)]


@pytest.mark.django_db
def test_add_living_language_page_renders(admin_client, languages):
    response = admin_client.get(reverse(ADD_LIVING_URL_NAME))

    assert response.status_code == 200
    assert response.context["page"] is None


@pytest.mark.django_db
def test_search_living_languages_requires_at_least_two_characters(
    admin_client, languages
):
    response = _search(admin_client, "d")

    assert response.context["page"] is None
    assert response.context["form"].errors["search_term"]


@pytest.mark.django_db
@pytest.mark.parametrize("term", ["danish", "DANISH", "dan", "tanska", "danska"])
def test_search_living_languages_matches_code_and_names_case_insensitively(
    admin_client, languages, term
):
    response = _search(admin_client, term)

    assert ("dan", "tanska", "danska", "Danish") in response.context["page"].object_list
    assert 'value="dan"' in response.content.decode()


@pytest.mark.django_db
def test_search_living_languages_shows_existing_languages_as_already_added(
    admin_client, languages
):
    response = _search(admin_client, "finnish")

    codes = [language.alpha_3 for language in response.context["page"]]
    assert "fin" in codes
    assert "fkv" in codes
    assert "fin" in response.context["existing_codes"]
    assert "fkv" not in response.context["existing_codes"]
    assert 'value="fin"' not in response.content.decode()
    assert 'value="fkv"' in response.content.decode()


@pytest.mark.django_db
def test_search_living_languages_excludes_languages_that_are_not_living(
    admin_client, languages
):
    response = _search(admin_client, "latin")

    codes = [language.alpha_3 for language in response.context["page"]]
    assert "lat" not in codes


@pytest.mark.django_db
def test_search_living_languages_paginates(admin_client, languages):
    first_page = _search(admin_client, "an").context["page"]
    last_page = _search(admin_client, "an", page=9999).context["page"]

    assert len(first_page) == 50
    assert first_page.has_next()
    assert not last_page.has_next()


@pytest.mark.django_db
def test_add_living_language_creates_language_with_translated_names(
    admin_client, languages
):
    response = admin_client.post(reverse(ADD_LIVING_URL_NAME), {"code": "dan"})

    language = Language.objects.get(alpha_3_code="dan")
    assert response.status_code == 302
    assert response.url == reverse(
        "admin:languages_language_change", args=(language.pk,)
    )
    assert language.safe_translation_getter("name", language_code="fi") == "tanska"
    assert language.safe_translation_getter("name", language_code="sv") == "danska"
    assert language.safe_translation_getter("name", language_code="en") == "Danish"


@pytest.mark.django_db
def test_add_living_language_reports_success(admin_client, languages):
    response = admin_client.post(
        reverse(ADD_LIVING_URL_NAME), {"code": "dan"}, follow=True
    )

    assert _messages(response) == ['Added language "Danish (dan)".']


@pytest.mark.django_db
def test_add_living_language_uses_english_name_when_translation_is_missing(
    admin_client, languages, monkeypatch
):
    monkeypatch.setattr(
        "languages.models.get_cldr_language_name",
        lambda language, parler_language: (
            None if parler_language == "fi" else "mocked Swedish name"
        ),
    )

    response = admin_client.post(
        reverse(ADD_LIVING_URL_NAME), {"code": "dan"}, follow=True
    )

    language = Language.objects.get(alpha_3_code="dan")
    assert language.safe_translation_getter("name", language_code="fi") == "Danish"
    assert (
        language.safe_translation_getter("name", language_code="sv")
        == "mocked Swedish name"
    )
    messages = _messages(response)
    assert len(messages) == 2
    success_message, fallback_message = messages
    assert success_message == 'Added language "Danish (dan)".'
    assert "The English name was used for fi translation" in fallback_message


@pytest.mark.django_db
def test_add_living_language_rejects_existing_language(admin_client, languages):
    language_count = Language.objects.count()

    response = admin_client.post(
        reverse(ADD_LIVING_URL_NAME), {"code": "fin"}, follow=True
    )

    assert response.redirect_chain == [(reverse(ADD_LIVING_URL_NAME), 302)]
    assert _messages(response) == ['Language "fin" already exists.']
    assert Language.objects.count() == language_count


@pytest.mark.django_db
@pytest.mark.parametrize("code", ["", "zzz"])
def test_add_living_language_rejects_invalid_code(admin_client, languages, code):
    language_count = Language.objects.count()

    response = admin_client.post(
        reverse(ADD_LIVING_URL_NAME), {"code": code}, follow=True
    )

    assert _messages(response) == [f'Invalid language code "{code}"']
    assert Language.objects.count() == language_count
