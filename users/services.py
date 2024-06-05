from django_ilmoitin.utils import send_notification

from users.models import Guardian
from users.notifications import NotificationType
from users.utils import get_communication_unsubscribe_ui_url


class GuardianEmailManagementNotificationService:
    @staticmethod
    def _send_notification(
        guardian: Guardian, notification_type: str, email: str, **kwargs
    ):
        context = kwargs.get("context", {})
        context["guardian"] = guardian
        context["unsubscribe_url"] = get_communication_unsubscribe_ui_url(
            guardian, guardian.language
        )
        send_notification(
            email, notification_type, context=context, language=guardian.language
        )

    @staticmethod
    def send_email_changed_notification(guardian: Guardian):
        """Send an email notification to guardian about a successful
        email change process. The email is now changed.

        Args:
            guardian (Guardian): the recipient guardian
        """
        GuardianEmailManagementNotificationService._send_notification(
            guardian, NotificationType.GUARDIAN_EMAIL_CHANGED, guardian.email
        )

    @staticmethod
    def send_email_update_token_notification(
        guardian: Guardian, email: str, verification_token_key: str
    ):
        """Send email update that contains the verification token key,
        that must be used to verify the new email during the change process.

        Args:
            guardian (Guardian): guardian whose email is being changed
            email (str): the new email address where the token is being sent
            verification_token_key (str): token to verify new email
        """
        GuardianEmailManagementNotificationService._send_notification(
            guardian,
            NotificationType.GUARDIAN_EMAIL_CHANGE_TOKEN,
            email,
            context={
                "verification_token": verification_token_key,
            },
        )
