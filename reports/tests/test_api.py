import base64
from datetime import date

import freezegun
import pytest
from django.contrib.auth import get_user_model
from guardian.shortcuts import assign_perm, remove_perm
from rest_framework.test import APIClient

from children.factories import ChildFactory, ChildWithGuardianFactory
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
def test_children_endpoint(user_api_client, snapshot, django_assert_max_num_queries):
    with freezegun.freeze_time("2021-02-02T12:00:00Z"):
        ChildWithGuardianFactory(
            birthdate=date(2021, 1, 1),
            postal_code="11111",
            relationship__guardian__language="fi",
            relationship__guardian__languages_spoken_at_home=["fin", None],
        )

    with freezegun.freeze_time("2021-03-03T01:00:00Z"):
        ChildWithGuardianFactory(
            birthdate=date(2021, 2, 2),
            postal_code="22222",
            relationship__guardian__language="sv",
            relationship__guardian__languages_spoken_at_home=[None],
        )

    # This guy's registration date should be 2021-04-05 in Helsinki time
    with freezegun.freeze_time("2021-04-04T23:00:00Z"):
        ChildWithGuardianFactory(
            birthdate=date(2020, 3, 3),
            postal_code="33333",
            relationship__guardian__language="en",
        )

    ChildFactory()  # This is an orphan child so she should not be in the results

    with django_assert_max_num_queries(6):
        response = user_api_client.get(LIST_ENDPOINT)
    assert response.status_code == 200, response.content

    snapshot.assert_match(response.json())
