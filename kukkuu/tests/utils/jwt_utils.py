import time
import uuid
from typing import Optional, TYPE_CHECKING

from django.conf import settings
from jose import jwt

if TYPE_CHECKING:
    from users.models import User as UserType


TEST_JWT_EXP_TIME_IN_SECONDS = 60


def get_epoch_timeframe_for_test_jwt():
    """Get test JWT valid timeframe as epoch times

    Returns:
        tuple[int, int]: issued at (epoch), expiration (epoch)
    """
    epoch_time = int(time.time())
    return epoch_time, epoch_time + TEST_JWT_EXP_TIME_IN_SECONDS


def generate_symmetric_test_jwt(
    user: "UserType",
    shared_secret_for_signature: Optional[str] = None,
    issuer="https://kukkuu-ui.test.hel.ninja",
    prefix="bearer",
):
    headers = {
        "alg": "HS256",
        "typ": "JWT",
        "kid": "zm1m8hQE6UACBzenpoINymuYRf0mL7Z4m-nVHpvy5Kc",
    }
    epoch_time, exp_epoch = get_epoch_timeframe_for_test_jwt()
    payload = {
        "iat": epoch_time,
        "auth_time": epoch_time,
        "exp": exp_epoch,
        "jti": uuid.uuid4().__str__(),
        "iss": issuer,
        "aud": "kukkuu-api-test",
        "sub": user.uuid.__str__(),
        "typ": "Bearer",
        "authorization": {"permissions": [{"scopes": ["access"]}]},
        "scope": "profile email",
        "email_verified": False,
        "amr": ["helsinki_tunnus"],
        "name": f"{user.first_name} {user.last_name}",
        "preferred_username": user.username,
        "given_name": user.first_name,
        "family_name": user.last_name,
        "email": user.email,
        "loa": "low",
    }
    token = jwt.encode(
        claims=payload,
        key=shared_secret_for_signature
        or settings.OIDC_BROWSER_TEST_API_TOKEN_AUTH["JWT_SIGN_SECRET"],
        headers=headers,
    )
    return f"{prefix} {token}"


def is_valid_256_bit_key(key_string: str):
    """Checks if the provided string represents a valid 256-bit key."""

    if not key_string or not isinstance(key_string, str):
        return False

    # Check if the string is a valid hexadecimal string
    if not all(c in "0123456789abcdefABCDEF" for c in key_string):
        return False

    # Check if the string has the expected length for a 256-bit key (32 bytes in hex)
    if len(key_string) != 64:
        return False

    return True
