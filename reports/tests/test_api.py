import base64
from datetime import date

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
            first_name="John",
            last_name="Doe",
            birthdate=date(2021, 1, 1),
            postal_code="11111",
            relationship__guardian__language="fi",
            relationship__guardian__languages_spoken_at_home=["fin", None],
            relationship__guardian__email="advocate@example.org",
        )

    with freezegun.freeze_time("2021-03-03T01:00:00Z"):
        ChildWithGuardianFactory(
            first_name="Isabella",
            last_name="Garcia",
            birthdate=date(2021, 2, 2),
            postal_code="22222",
            relationship__guardian__language="sv",
            relationship__guardian__languages_spoken_at_home=[None],
            relationship__guardian__email="parent@example.org",
        )

    # This guy's registration date should be 2021-04-05 in Helsinki time
    with freezegun.freeze_time("2021-04-04T23:00:00Z"):
        ChildWithGuardianFactory(
            first_name="Jane",
            last_name="Doe",
            birthdate=date(2020, 3, 3),
            postal_code="33333",
            relationship__guardian__language="en",
            relationship__guardian__email="",
        )

    with freezegun.freeze_time("2021-04-05T21:05:00Z"):
        ChildWithTwoGuardiansFactory(
            first_name="First name",
            last_name="Last name",
            birthdate=date(2020, 3, 3),
            postal_code="33333",
            relationship__guardian__language="en",
            relationship__guardian__email="guardian@example.org",
            relationship2__guardian__language="sv",
            relationship2__guardian__email="advocate@example.org",
        )

    ChildFactory()  # This is an orphan child so she should not be in the results

    with django_assert_max_num_queries(6):
        response = user_api_client.get(LIST_ENDPOINT)
    assert response.status_code == 200, response.content

    snapshot.assert_match(response.json())
