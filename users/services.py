from typing import Optional, Union

from django.db.models import QuerySet
from django.template import Context, Template
from django_ilmoitin.utils import send_notification

from users.models import Guardian
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
        from users.notifications import NotificationType

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
        from users.notifications import NotificationType

        GuardianEmailManagementNotificationService._send_notification(
            guardian,
            NotificationType.GUARDIAN_EMAIL_CHANGE_TOKEN,
            email,
            context={
                "verification_token": verification_token_key,
            },
        )


class AuthServiceNotificationService:
    @staticmethod
    def _send_auth_service_is_changing_notification(
        guardian: Guardian, date_of_change_str: Optional[str] = None
    ):
        """Send the auth service is changing notification to a guardian.

        Args:
            guardian (Guardian): the guardian instance
            date_of_change_str (Optional[str], optional): Date or datetime
                in string format. Defaults to None.
                The actual default should be given in the notification template.
        """
        from users.notifications import NotificationType

        send_notification(
            guardian.email,
            NotificationType.USER_AUTH_SERVICE_IS_CHANGING,
            context={
                "guardian": guardian,
                "date_of_change_str": date_of_change_str,
                "children_event_history_markdown": (
                    AuthServiceNotificationService.generate_children_event_history_markdown(  # noqa
                        guardian
                    )
                ),
            },
            language=guardian.language,
        )

    @staticmethod
    def send_user_auth_service_is_changing_notifications(
        guardians: Optional[Union[QuerySet, list[Guardian]]] = None,
        date_of_change_str: Optional[str] = None,
    ):
        """Send user authentication service is changing notifications
        to guariands as recipients.

        If the guardian list is not explicitly given
        the queryset result of
        `Guardian.objects.for_auth_service_is_changing_notification()`
        will be used as a default.

        Args:
            guardians (Optional[Union[QuerySet, list[Guardian]]], optional):
                explicit list of guardians as recipients. Defaults to None.
            date_of_change_str (Optional[str], optional): Date or datetime
                in string format. Defaults to None.
                The actual default should be given in the notification template.
        """
        if guardians is None:
            guardians = Guardian.objects.for_auth_service_is_changing_notification()

        for guardian in guardians:
            AuthServiceNotificationService._send_auth_service_is_changing_notification(
                guardian, date_of_change_str
            )

    @staticmethod
    def generate_children_event_history_markdown(guardian: Guardian):
        """Generates a Markdown string listing a guardian's children's enrolments."""

        # NOTE: This is markdown, so the line changes and white spaces are important!
        template_string = """
{% for child in guardian.children.all %}# {{ child.name }}
{% for enrolment in child.enrolments.all|dictsort:"occurrence.time" %}1. **{{ enrolment.occurrence.event.name }}:** {{ enrolment.occurrence.time|date:"j.n.Y H:i" }}{% if enrolment.occurrence.event.short_description %}
{{enrolment.occurrence.event.short_description}}{% endif %}
{% endfor %}
{% endfor %}
"""  # noqa

        template = Template(template_string)
        context = Context({"guardian": guardian})
        return template.render(context).strip()
