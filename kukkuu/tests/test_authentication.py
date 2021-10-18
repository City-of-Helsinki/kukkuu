from contextlib import contextmanager
from unittest import mock

import requests
from django.contrib.auth.models import AnonymousUser
from helusers.authz import UserAuthorization

from common.tests.utils import assert_permission_denied
from users.factories import GuardianFactory

MY_PROFILE_QUERY = """
query MyProfile {
  myProfile {
    email
  }
}
"""


@contextmanager
def set_authenticated_user(user):
    with mock.patch(
        "helusers.oidc.RequestJWTAuthentication.authenticate",
        return_value=UserAuthorization(user=user, api_token_payload={}),
    ):
        yield


def graphql_request(live_server, query=MY_PROFILE_QUERY):
    return requests.post(live_server.url + "/graphql", json={"query": query})


def test_authentication_unauthenticated(live_server):
    with set_authenticated_user(AnonymousUser()):
        with mock.patch("sentry_sdk.capture_exception") as sentry:
            response = graphql_request(live_server)

            assert_permission_denied(response.json())
            # PermissionDenied should not be sent to Sentry
            sentry.assert_not_called()


def test_authentication_authenticated(live_server):
    guardian = GuardianFactory(email="gustavo.guardian@example.com")

    with set_authenticated_user(guardian.user):
        response = graphql_request(live_server)
        assert (
            response.json()["data"]["myProfile"]["email"]
            == "gustavo.guardian@example.com"
        )
