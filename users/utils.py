from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django_ilmoitin.utils import send_notification

from kukkuu.exceptions import InvalidEmailFormatError, VerificationTokenInvalidError
from users.models import Guardian, User
from users.notifications import NotificationType
from verification_tokens.models import VerificationToken


def send_guardian_email_changed_notification(guardian: Guardian):
    send_notification(
        guardian.email,
        NotificationType.GUARDIAN_EMAIL_CHANGED,
        context={"guardian": guardian},
        language=guardian.language,
    )


def send_guardian_email_update_token_notification(
    guardian: Guardian, email: str, verification_token_key: str
):
    send_notification(
        email,
        NotificationType.GUARDIAN_EMAIL_CHANGE_TOKEN,
        context={"guardian": guardian, "verification_token": verification_token_key},
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
