from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django_ilmoitin.utils import send_notification

from kukkuu.consts import DEFAULT_LANGUAGE
from kukkuu.exceptions import InvalidEmailFormatError, VerificationTokenInvalidError
from users.models import Guardian, User
from verification_tokens.models import VerificationToken


def send_guardian_email_changed_notification(guardian: Guardian):
    from users.notifications import NotificationType

    send_notification(
        guardian.email,
        NotificationType.GUARDIAN_EMAIL_CHANGED,
        context={
            "guardian": guardian,
            "unsubscribe_url": get_marketing_unsubscribe_ui_url(
                guardian, guardian.language
            ),
        },
        language=guardian.language,
    )


def send_guardian_email_update_token_notification(
    guardian: Guardian, email: str, verification_token_key: str
):
    from users.notifications import NotificationType

    send_notification(
        email,
        NotificationType.GUARDIAN_EMAIL_CHANGE_TOKEN,
        context={
            "guardian": guardian,
            "verification_token": verification_token_key,
            "unsubscribe_url": get_marketing_unsubscribe_ui_url(
                guardian, guardian.language
            ),
        },
        language=guardian.language,
    )


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


def get_marketing_unsubscribe_ui_url(
    guardian: Guardian,
    language: Optional[str] = DEFAULT_LANGUAGE,
    verification_token: Optional[VerificationToken] = None,
):
    if not verification_token:
        verification_token = guardian.user.create_subscriptions_management_auth_token()
    return "{}/{}/profile/subscriptions?authToken={}".format(
        settings.KUKKUU_UI_BASE_URL,
        language,
        verification_token.key,
    )
