import base64

import freezegun
import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from guardian.shortcuts import assign_perm, remove_perm
from rest_framework.test import APIClient

from children.factories import (
    ChildFactory,
    ChildWithGuardianFactory,
    ChildWithTwoGuardiansFactory,
)
from languages.models import Language
from reports.api import get_primary_contact_language
from reports.drf_permissions import ACCESS_REPORT_API_PERM

LIST_ENDPOINT = "/reports/children/"


@pytest.fixture(autouse=True)
def languages():
    for code in ("fin", "swe", "eng"):
        Language.objects.create_from_language_code(code)
    Language.objects.create_option_other()


@pytest.fixture
def user():
    user = get_user_model().objects.create_user(
        username="test_user",
        password="test_password",
    )
    assign_perm(ACCESS_REPORT_API_PERM, user)
    return user


@pytest.fixture
def user_api_client(user):
    api_client = APIClient()
    api_client.user = user
    credentials = b"test_user:test_password"
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Basic {base64.b64encode(credentials).decode('ascii')}"
    )
    return api_client


@pytest.mark.django_db
def test_children_endpoint_not_authenticated(user):
    response = APIClient().get(LIST_ENDPOINT)
    assert response.status_code == 401


@pytest.mark.django_db
def test_children_endpoint_no_permission(user_api_client):
    remove_perm(ACCESS_REPORT_API_PERM, user_api_client.user)
    response = user_api_client.get(LIST_ENDPOINT)
    assert response.status_code == 403


@pytest.mark.django_db
@override_settings(
    # Must be the same as in CI pipeline for the snapshot to be an exact match:
    KUKKUU_HASHID_SALT="almosttopsecret123"
)
def test_children_endpoint(user_api_client, snapshot, django_assert_max_num_queries):
    with freezegun.freeze_time("2021-02-02T12:00:00Z"):
        ChildWithGuardianFactory(
            name="Doe John",
            birthyear=2021,
            postal_code="11111",
            relationship__guardian__language="fi",
            relationship__guardian__languages_spoken_at_home=["fin", None],
            relationship__guardian__email="advocate@example.org",
        )

    with freezegun.freeze_time("2021-03-03T01:00:00Z"):
        ChildWithGuardianFactory(
            name="Garcia Isabella",
            birthyear=2021,
            postal_code="22222",
            relationship__guardian__language="sv",
            relationship__guardian__languages_spoken_at_home=[None],
            relationship__guardian__email="parent@example.org",
        )

    # This guy's registration date should be 2021-04-05 in Helsinki time
    with freezegun.freeze_time("2021-04-04T23:00:00Z"):
        ChildWithGuardianFactory(
            name="Doe Jane",
            birthyear=2020,
            postal_code="33333",
            relationship__guardian__language="en",
            relationship__guardian__email="something@to-fool-factoryboy.net",
        )

    with freezegun.freeze_time("2021-04-05T21:05:00Z"):
        ChildWithTwoGuardiansFactory(
            name="Last name First name",
            birthyear=2020,
            postal_code="44444",
            relationship__guardian__language="en",
            relationship__guardian__email="guardian@example.org",
            relationship2__guardian__language="sv",
            relationship2__guardian__email="advocate@example.org",
        )

    ChildFactory()  # This is an orphan child so she should not be in the results

    with django_assert_max_num_queries(7):
        response = user_api_client.get(LIST_ENDPOINT)
    assert response.status_code == 200, response.content

    json_data = response.json()

    # The result set should be ordered by 'name'
    assert [child["postal_code"] for child in json_data] == [
        "33333",
        "11111",
        "22222",
        "44444",
    ]

    snapshot.assert_match(json_data)


@pytest.mark.parametrize(
    "contact_languages,language",
    [
        [["en", "sv", "fi"], "fi"],
        [["fi", "en", "sv"], "fi"],
        [["en", "sv"], "en"],
        [["en"], "en"],
        [["fi", "en"], "fi"],
        [["sv"], "sv"],
    ],
)
@pytest.mark.django_db
def test_get_primary_contact_language(contact_languages, language):
    assert get_primary_contact_language(contact_languages) == language


@pytest.mark.django_db
def test_filter_by_is_obsolete(user_api_client):
    ChildWithGuardianFactory(relationship__guardian__user__is_obsolete=False)
    ChildWithGuardianFactory(relationship__guardian__user__is_obsolete=True)

    # Test filtering by is_obsolete=True, to fetch all child that are obsolete
    response = user_api_client.get(LIST_ENDPOINT + "?is_obsolete=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["is_obsolete"] is True

    # Test filtering by is_obsolete=False
    response = user_api_client.get(LIST_ENDPOINT + "?is_obsolete=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["is_obsolete"] is False

    response = user_api_client.get(LIST_ENDPOINT)
    assert response.status_code == 200
    assert len(response.json()) == 2
