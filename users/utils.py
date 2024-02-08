from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django_ilmoitin.utils import send_notification

from kukkuu.exceptions import InvalidEmailFormatError, VerificationTokenInvalidError
from users.notifications import NotificationType
from verification_tokens.models import VerificationToken

User = get_user_model()


def send_guardian_email_changed_notification(guardian):
    send_notification(
        guardian.email,
        NotificationType.GUARDIAN_EMAIL_CHANGED,
        context={"guardian": guardian},
        language=guardian.language,
    )


def validate_email_verification_token(user: User, verification_token_key: str):
    verification_token = VerificationToken.objects.filter(
        user=user,
        verification_type=VerificationToken.VERIFICATION_TYPE_EMAIL_VERIFICATION,
        key=verification_token_key,
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
