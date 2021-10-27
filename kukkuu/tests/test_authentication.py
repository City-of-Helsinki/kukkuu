from contextlib import contextmanager
from unittest import mock

import requests
from django.contrib.auth.models import AnonymousUser
from helusers.authz import UserAuthorization
from helusers.oidc import AuthenticationError
from jose import ExpiredSignatureError

from common.tests.utils import assert_match_error_code, assert_permission_denied
from kukkuu.consts import AUTHENTICATION_ERROR, AUTHENTICATION_EXPIRED_ERROR
from users.factories import GuardianFactory

HELUSERS_AUTHENTICATE = "helusers.oidc.RequestJWTAuthentication.authenticate"
SENTRY_CAPTURE_EXCEPTION = "sentry_sdk.capture_exception"

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
        HELUSERS_AUTHENTICATE,
        return_value=UserAuthorization(user=user, api_token_payload={}),
    ):
        yield


def graphql_request(live_server, query=MY_PROFILE_QUERY):
    return requests.post(live_server.url + "/graphql", json={"query": query})


def test_authentication_unauthenticated(live_server):
    with set_authenticated_user(AnonymousUser()):
        with mock.patch(SENTRY_CAPTURE_EXCEPTION) as sentry:
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


def test_authentication_error(live_server):
    with mock.patch(SENTRY_CAPTURE_EXCEPTION) as sentry:
        with mock.patch(
            HELUSERS_AUTHENTICATE,
            side_effect=AuthenticationError("JWT verification failed."),
        ):
            response = graphql_request(live_server)
            assert_match_error_code(response.json(), AUTHENTICATION_ERROR)
            sentry.assert_called()


def test_authentication_expired_error(live_server):
    def expired_token_authenticate(*args):
        try:
            raise ExpiredSignatureError()
        except Exception:
            raise AuthenticationError("JWT verification failed.")

    with mock.patch(SENTRY_CAPTURE_EXCEPTION) as sentry:
        with mock.patch(
            HELUSERS_AUTHENTICATE,
            side_effect=expired_token_authenticate,
        ):
            response = graphql_request(live_server)
            assert_match_error_code(response.json(), AUTHENTICATION_EXPIRED_ERROR)
            sentry.assert_not_called()
