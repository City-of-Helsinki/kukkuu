import logging
from typing import Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from helusers.authz import UserAuthorization
from helusers.jwt import JWT, ValidationError
from helusers.oidc import AuthenticationError, RequestJWTAuthentication
from helusers.settings import api_token_auth_settings
from helusers.user_utils import get_or_create_user
from jose import jwt as jose_jwt

from kukkuu.tests.utils.jwt_utils import is_valid_256_bit_key

logger = logging.getLogger(__name__)


class ApiTokenAuthSettings:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class BrowserTestAwareJWTAuthentication(RequestJWTAuthentication):
    def __init__(self):
        super().__init__()
        combined_settings = {
            **api_token_auth_settings._settings,
            **settings.OIDC_BROWSER_TEST_API_TOKEN_AUTH,
        }
        self._api_token_auth_settings = ApiTokenAuthSettings(**combined_settings)
        self.algorithms = ["HS256"]

        if self._api_token_auth_settings.ENABLED:
            if not self._api_token_auth_settings.ISSUER:
                raise ImproperlyConfigured(
                    "ISSUER must be configured when test JWT auth is enabled."
                )
            if not is_valid_256_bit_key(self._api_token_auth_settings.JWT_SIGN_SECRET):
                raise ImproperlyConfigured(
                    "JWT_SIGN_SECRET (JWT secret key) must be 256 bits"
                )

    def _get_auth_header_jwt(self, request):
        """Looks for a JWT from the request's "Authorization" header.

        If the header is not found, or it doesn't contain a JWT, returns None.
        If the header is found and contains a JWT then returns a JWT.

        Args:
            request: the request object

        Returns:
            JWT|None: JWT if the Authorization header contains one. Otherwise None.
        """
        auth_header = request.headers["Authorization"]

        if not auth_header:
            return None

        auth_scheme, jwt_value = auth_header.split()
        if auth_scheme.lower() != "bearer":
            return None

        return JWT(jwt_value, self._api_token_auth_settings)

    def _validate_symmetrically_signed_jwt(self, jwt: JWT):
        """
        Validate a symmetrically signed JWT that is signed by a shared secret.

        NOTE: This function is implemented since the `django_helusers`
        does not verify symmetrically signed JWT that are signed by a shared secret.
        The `helusers` always uses a issuer specific `OIDCConfig` that fetches the
        keys from a server (from a path "/.well-known/openid-configuration").
        """
        logger.debug(
            "Validating a symmetrically signed test JWT",
            extra={"jwt_claims": jwt.claims if jwt else None},
        )
        try:
            jwt.validate_issuer()
        except ValidationError as e:
            raise AuthenticationError(str(e)) from e
        try:
            jose_jwt.decode(
                token=jwt._encoded_jwt,
                key=self._api_token_auth_settings.JWT_SIGN_SECRET,
                audience=jwt.claims.get("aud"),
                issuer=jwt.claims.get("iss"),
                subject=jwt.claims.get("sub"),
                algorithms=self.algorithms,
            )
        except ValidationError as e:
            raise AuthenticationError(str(e)) from e
        except Exception:
            raise AuthenticationError("JWT verification failed.")

    def has_auth_token_for_testing(self, request) -> Optional[JWT]:
        """Checks whether the request contains a JWT which is
        issued for end-to-end browser testing use only.

        Args:
            request: the request object.

        Returns:
            Optional[JWT]: JWT if it is issued for brower test use. Otherwise None.
        """
        jwt = self._get_auth_header_jwt(request)
        if jwt.claims.get("iss") not in self._api_token_auth_settings.ISSUER:
            return None
        return jwt

    def authenticate_test_user(self, jwt: JWT):
        """Authenticate a user who is sending the browser test request.

        Args:
            jwt (JWT): the JWT issued for browser testing use that is
                attached into the request.

        Returns:
            UserAuthorization: user authorization instance.
        """
        logger.info("Authenticating with a test JWT!")
        self._validate_symmetrically_signed_jwt(jwt)
        logger.debug(
            "The symmetrically signed JWT was valid.",
            extra={"jwt_claims": jwt.claims if jwt else None},
        )
        user = get_or_create_user(jwt.claims, oidc=True)
        logger.debug(
            "The user %s returned from get_or_create_user",
            user,
            extra={"user": getattr(user, "__dict__", str(user))},
        )
        return UserAuthorization(user, jwt.claims)

    def authenticate(self, request):
        """
        Looks for a JWT from the request's "Authorization" header.
        If the header is not found, or it doesn't contain a JWT, returns None.
        If the header is found and contains a JWT then the JWT gets verified.

        Test whether the JWT is issued for the end-to-end browser test use.
        IF the JWT is for test use, then handle it with `authenticate_test_user`,
        since the `django_helusers` does not support symmetrically signed JWT.

        If verification passes, takes a user's id from the JWT's "sub" claim.
        Creates a User if it doesn't already exist.
        On success returns a UserAuthorization object.
        Raises an AuthenticationError on authentication failure.

        """
        if self._api_token_auth_settings.ENABLED:
            if jwt := self.has_auth_token_for_testing(request):
                return self.authenticate_test_user(jwt)
        return super().authenticate(request)
