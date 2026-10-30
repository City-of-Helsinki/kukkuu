import pytest
from django.contrib.admin import helpers
from django.contrib.admin.utils import quote
from django.urls import reverse

from events.factories import EventFactory
from tags.factories import ThemePathFactory
from tags.models import ThemePath

ADD_URL = reverse("admin:tags_themepath_add")


def _change_url(theme_path):
    return reverse("admin:tags_themepath_change", args=[quote(theme_path.pk)])


def _delete_url(theme_path):
    return reverse("admin:tags_themepath_delete", args=[quote(theme_path.pk)])


def _delete_translation_url(theme_path, language_code):
    return reverse(
        "admin:tags_themepath_delete_translation",
        args=[quote(theme_path.pk), language_code],
    )


@pytest.mark.django_db
def test_theme_path_admin_add_creates_theme_path(admin_client):
    response = admin_client.post(
        f"{ADD_URL}?language=fi",
        {
            "slug": "nature_walks",
            "name": "Luontopolut",
            "description": "",
            "sort_order": "4",
        },
    )

    assert response.status_code == 302
    theme_path = ThemePath.objects.get(slug="nature_walks")
    assert theme_path.safe_translation_getter("name", language_code="fi") == (
        "Luontopolut"
    )


@pytest.mark.django_db
def test_theme_path_admin_add_requires_finnish_translation(admin_client):
    response = admin_client.post(
        f"{ADD_URL}?language=en",
        {"slug": "nature_walks", "name": "Nature walks", "description": ""},
    )

    assert response.status_code == 200
    assert "A Finnish translation is required." in response.content.decode()
    assert not ThemePath.objects.filter(slug="nature_walks").exists()


@pytest.mark.django_db
def test_theme_path_admin_can_add_other_language_when_finnish_exists(admin_client):
    theme_path = ThemePathFactory(name="Suomeksi")

    response = admin_client.post(
        f"{_change_url(theme_path)}?language=sv",
        {"name": "På svenska", "description": ""},
    )

    assert response.status_code == 302
    theme_path.refresh_from_db()
    assert theme_path.safe_translation_getter("name", language_code="sv") == (
        "På svenska"
    )


@pytest.mark.django_db
def test_theme_path_admin_add_rejects_existing_slug(admin_client):
    ThemePathFactory(slug="nature_walks")

    response = admin_client.post(
        f"{ADD_URL}?language=fi",
        {"slug": "nature_walks", "name": "Luontopolut", "description": ""},
    )

    assert response.status_code == 200
    assert "slug" in response.context["adminform"].form.errors


@pytest.mark.django_db
def test_theme_path_admin_slug_is_read_only_on_change(admin_client):
    theme_path = ThemePathFactory(slug="nature_walks")

    response = admin_client.post(
        f"{_change_url(theme_path)}?language=fi",
        {"slug": "renamed", "name": "Uusi nimi", "description": ""},
    )

    assert response.status_code == 302
    assert not ThemePath.objects.filter(slug="renamed").exists()
    assert ThemePath.objects.get(slug="nature_walks").name == "Uusi nimi"


@pytest.mark.django_db
def test_theme_path_admin_refuses_deleting_finnish_translation(admin_client):
    theme_path = ThemePathFactory(
        translations={"fi": {"name": "Suomeksi"}, "sv": {"name": "På svenska"}}
    )

    response = admin_client.post(
        _delete_translation_url(theme_path, "fi"), {"post": "yes"}, follow=True
    )

    messages = [str(message) for message in response.context["messages"]]
    assert messages == ["The Finnish translation can't be deleted."]
    theme_path.refresh_from_db()
    assert theme_path.has_translation("fi")


@pytest.mark.django_db
@pytest.mark.parametrize("language_code", ["sv", "en"])
def test_theme_path_admin_deletes_other_translations(admin_client, language_code):
    theme_path = ThemePathFactory(
        translations={
            "fi": {"name": "Suomeksi"},
            "sv": {"name": "På svenska"},
            "en": {"name": "In English"},
        }
    )

    response = admin_client.post(
        _delete_translation_url(theme_path, language_code), {"post": "yes"}
    )

    assert response.status_code == 302
    theme_path.refresh_from_db()
    assert not theme_path.has_translation(language_code)
    assert theme_path.has_translation("fi")


@pytest.mark.django_db
def test_theme_path_admin_delete_is_refused_when_used_by_events(admin_client):
    theme_path = ThemePathFactory()
    event = EventFactory(theme_paths=[theme_path])
    url = _delete_url(theme_path)

    response = admin_client.get(url)

    assert len(response.context["protected"]) == 1
    assert str(event) in response.context["protected"][0]

    response = admin_client.post(url, {"post": "yes"})

    assert response.status_code == 200
    assert ThemePath.objects.filter(pk=theme_path.pk).exists()
    assert list(event.theme_paths.all()) == [theme_path]


@pytest.mark.django_db
def test_theme_path_admin_bulk_delete_is_refused_when_used_by_events(admin_client):
    unused, used = ThemePathFactory.create_batch(2)
    EventFactory(theme_paths=[used])

    response = admin_client.post(
        reverse("admin:tags_themepath_changelist"),
        {
            "action": "delete_selected",
            helpers.ACTION_CHECKBOX_NAME: [unused.pk, used.pk],
            "post": "yes",
        },
    )

    assert response.status_code == 200
    assert ThemePath.objects.filter(pk__in=[unused.pk, used.pk]).count() == 2


@pytest.mark.django_db
def test_theme_path_admin_deletes_unused_theme_path(admin_client):
    theme_path = ThemePathFactory()

    response = admin_client.post(
        _delete_url(theme_path),
        {"post": "yes"},
    )

    assert response.status_code == 302
    assert not ThemePath.objects.filter(pk=theme_path.pk).exists()
