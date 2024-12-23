from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from kukkuu.exceptions import InvalidEmailFormatError, VerificationTokenInvalidError
from users.models import Guardian, User
from verification_tokens.models import VerificationToken


def validate_email_verification_token(
    user: User, email: str, verification_token_key: str
):
    verification_token = VerificationToken.objects.filter(
        user=user,
        verification_type=VerificationToken.VERIFICATION_TYPE_EMAIL_VERIFICATION,
        key=verification_token_key,
        email=email,
    ).first()
    if not verification_token or not verification_token.is_valid():
        raise VerificationTokenInvalidError("The verification token is invalid")


def validate_guardian_email(email: str):
    try:
        validate_email(email)
    except ValidationError:
        raise InvalidEmailFormatError("Invalid email format")


def validate_guardian_data(guardian_data: dict):
    if "email" in guardian_data:
        validate_guardian_email(guardian_data["email"])
    return guardian_data


def get_communication_unsubscribe_ui_url(
    guardian: Guardian,
    language: Optional[str] = None,
    verification_token: Optional[VerificationToken] = None,
):
    if not language:
        language = settings.LANGUAGE_CODE
    if not verification_token:
        verification_token = guardian.user.create_subscriptions_management_auth_token()
    return "{}/{}/profile/subscriptions?authToken={}".format(
        settings.KUKKUU_UI_BASE_URL,
        language,
        verification_token.key,
    )
