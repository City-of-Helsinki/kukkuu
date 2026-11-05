import pytest
from django.contrib.admin.utils import quote
from django.urls import reverse


def _url(*, model, action, args=(), language=None):
    opts = model._meta
    url = reverse(f"admin:{opts.app_label}_{opts.model_name}_{action}", args=args)
    return f"{url}?language={language}" if language else url


def _add_url(tag_model, language):
    return _url(model=tag_model, action="add", language=language)


def _change_url(tag, language):
    return _url(
        model=type(tag), action="change", args=[quote(tag.pk)], language=language
    )


def _delete_url(tag):
    return _url(model=type(tag), action="delete", args=[quote(tag.pk)])


def _delete_translation_url(tag, language_code):
    return _url(
        model=type(tag),
        action="delete_translation",
        args=[quote(tag.pk), language_code],
    )


@pytest.mark.django_db
def test_tag_admin_add_creates_tag(admin_client, tag_model):
    response = admin_client.post(
        _add_url(tag_model, language="fi"),
        {
            "slug": "nature_walks",
            "name": "Luontopolut",
            "description": "",
            "sort_order": "4",
        },
    )

    assert response.status_code == 302
    tag = tag_model.objects.get(slug="nature_walks")
    assert tag.safe_translation_getter("name", language_code="fi") == "Luontopolut"


@pytest.mark.django_db
def test_tag_admin_add_requires_finnish_translation(admin_client, tag_model):
    response = admin_client.post(
        _add_url(tag_model, language="en"),
        {"slug": "nature_walks", "name": "Nature walks", "description": ""},
    )

    assert response.status_code == 200
    assert (
        "A default language (fi) translation is required." in response.content.decode()
    )
    assert not tag_model.objects.filter(slug="nature_walks").exists()


@pytest.mark.django_db
def test_tag_admin_can_add_other_language_when_finnish_exists(admin_client, tag_model):
    tag = tag_model.objects.create(slug="nature_walks")
    tag.create_translation("fi", name="Suomeksi")

    response = admin_client.post(
        _change_url(tag, language="sv"),
        {"name": "På svenska", "description": ""},
    )

    assert response.status_code == 302
    tag.refresh_from_db()
    assert tag.safe_translation_getter("name", language_code="sv") == "På svenska"


@pytest.mark.django_db
def test_tag_admin_add_rejects_existing_slug(admin_client, tag_model):
    tag_model.objects.create(slug="nature_walks")

    response = admin_client.post(
        _add_url(tag_model, language="fi"),
        {"slug": "nature_walks", "name": "Luontopolut", "description": ""},
    )

    assert response.status_code == 200
    assert "slug" in response.context["adminform"].form.errors


@pytest.mark.django_db
def test_tag_admin_slug_is_read_only_on_change(admin_client, tag_model):
    tag = tag_model.objects.create(slug="nature_walks")

    response = admin_client.post(
        _change_url(tag, language="fi"),
        {"slug": "renamed", "name": "Uusi nimi", "description": ""},
    )

    assert response.status_code == 302
    assert not tag_model.objects.filter(slug="renamed").exists()
    assert tag_model.objects.get(slug="nature_walks").name == "Uusi nimi"


@pytest.mark.django_db
def test_tag_admin_refuses_deleting_finnish_translation(admin_client, tag_model):
    tag = tag_model.objects.create(slug="nature_walks")
    tag.create_translation("fi", name="Suomeksi")
    tag.create_translation("sv", name="På svenska")

    response = admin_client.post(
        _delete_translation_url(tag, "fi"), {"post": "yes"}, follow=True
    )

    messages = [str(message) for message in response.context["messages"]]
    assert messages == ["The default language (fi) translation can not be deleted."]
    tag.refresh_from_db()
    assert tag.has_translation("fi")


@pytest.mark.django_db
@pytest.mark.parametrize("language_code", ["sv", "en"])
def test_tag_admin_deletes_other_translations(admin_client, tag_model, language_code):
    tag = tag_model.objects.create(slug="nature_walks")
    tag.create_translation("fi", name="Suomeksi")
    tag.create_translation("sv", name="På svenska")
    tag.create_translation("en", name="In English")

    response = admin_client.post(
        _delete_translation_url(tag, language_code), {"post": "yes"}
    )

    assert response.status_code == 302
    tag.refresh_from_db()
    assert not tag.has_translation(language_code)
    assert tag.has_translation("fi")


@pytest.mark.django_db
def test_tag_admin_deletes_unused_tag(admin_client, tag_model):
    tag = tag_model.objects.create(slug="nature_walks")

    response = admin_client.post(_delete_url(tag), {"post": "yes"})

    assert response.status_code == 302
    assert not tag_model.objects.filter(pk=tag.pk).exists()
