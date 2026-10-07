import pytest
from django import forms
from django.urls import reverse

from events.factories import EventFactory, OccurrenceFactory


def _get_url_form_fields(response) -> list[forms.URLField]:
    """Get the URL form fields of the admin change form and its inline forms."""
    admin_forms = [response.context["adminform"].form] + [
        inline_admin_formset.formset.empty_form
        for inline_admin_formset in response.context["inline_admin_formsets"]
    ]
    return [
        field
        for form in admin_forms
        for field in form.fields.values()
        if isinstance(field, forms.URLField)
    ]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj_factory",
    [EventFactory, OccurrenceFactory],
    ids=["event", "occurrence"],
)
def test_admin_url_fields_assume_https(admin_client, obj_factory, url_field_count):
    """Test the usages of AssumeHttpsURLFieldAdminMixin"""
    obj = obj_factory()
    opts = obj._meta

    response = admin_client.get(
        reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[obj.pk])
    )

    assert response.status_code == 200
    url_fields = _get_url_form_fields(response)
    assert url_fields
    for url_field in url_fields:
        assert url_field.clean("example.com") == "https://example.com"
