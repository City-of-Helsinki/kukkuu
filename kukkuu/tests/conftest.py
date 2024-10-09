import secrets
from typing import Optional

import pytest

from kukkuu.service import get_hashid_service
from kukkuu.tests.utils.jwt_utils import generate_symmetric_test_jwt
from users.factories import UserFactory
from users.models import User


@pytest.fixture
def hashids():
    return get_hashid_service()


@pytest.fixture(autouse=True)
def oidc_browser_test_api_token_auth_settings(settings):
    settings.OIDC_BROWSER_TEST_API_TOKEN_AUTH = {
        "ENABLED": True,
        "AUDIENCE": ["kukkuu-api-dev", "profile-api-test", "kukkuu-admin-ui-test"],
        "API_SCOPE_PREFIX": "",
        "REQUIRE_API_SCOPE_FOR_AUTHENTICATION": False,
        "API_AUTHORIZATION_FIELD": "authorization.permissions.scopes",
        "ISSUER": "https://kukkuu-ui.test.hel.ninja",
        "JWT_SIGN_SECRET": secrets.token_bytes(32).hex(),
    }


@pytest.fixture
def get_browser_test_bearer_token_for_user(oidc_browser_test_api_token_auth_settings):
    """Returns a test JWT token generator function.

    The generator function returns a signed bearer token to authenticate through
    the authentcation made for browser testing."""

    def generate_test_jwt_token(user: Optional[User] = None):
        user = user or UserFactory.build()
        return generate_symmetric_test_jwt(user)

    return generate_test_jwt_token
