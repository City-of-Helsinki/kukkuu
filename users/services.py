from typing import Optional, Union

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.template import Context, Template
from django_ilmoitin.utils import send_notification

from users.models import Guardian
from users.utils import get_communication_unsubscribe_ui_url

User = get_user_model()


class GuardianEmailChangeNotificationService:
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

        GuardianEmailChangeNotificationService._send_notification(
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

        GuardianEmailChangeNotificationService._send_notification(
            guardian,
            NotificationType.GUARDIAN_EMAIL_CHANGE_TOKEN,
            email,
            context={
                "verification_token": verification_token_key,
            },
        )


CHILDREN_EVENT_HISTORY_MARKDOWN_TEMPLATE = """
{% for child in guardian.children.all %}# {{ child.name }}

{% for enrolment in child.enrolments.all|dictsort:"occurrence.time" %}
{{ forloop.counter }}. **{{ enrolment.occurrence.event.name }}:** {{ enrolment.occurrence.time|date:"j.n.Y H:i" }}{% if enrolment.occurrence.event.short_description %}

    {{enrolment.occurrence.event.short_description}}
{% endif %}
{% endfor %}

{% endfor %}
"""  # noqa E501


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
        obsolete_handled_users: bool = False,
        batch_size: int = 1000,
    ) -> None:
        """Send user authentication service is changing notifications
        to guardians as recipients and optionally mark the handled users
        as obsolete.

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
            obsolete_handled_users (bool, optional): Should the users
                who have been handled be marked as obsolete. Defaults to False.
            batch_size (int, optional): The batch size for queryset iteration.
                Defaults to 1000.
        """
        if guardians is None:
            guardians = Guardian.objects.prefetch_related(
                "children",
            ).for_auth_service_is_changing_notification()

        handled_user_ids = []
        _notify_function = (
            AuthServiceNotificationService._send_auth_service_is_changing_notification
        )

        try:
            # Use iterator to reduce memory usage
            for guardian in guardians.iterator(chunk_size=batch_size):
                _notify_function(guardian, date_of_change_str)
                handled_user_ids.append(guardian.user_id)
        finally:
            # This will be executed even if an exception is raised
            if obsolete_handled_users:
                # Mark the handled users as obsolete in batches
                # to limit SQL update query size
                paginator = Paginator(handled_user_ids, batch_size)
                for page_num in paginator.page_range:
                    page_of_user_ids = paginator.page(page_num).object_list
                    User.objects.filter(id__in=page_of_user_ids).update(
                        is_obsolete=True
                    )

    @staticmethod
    def generate_children_event_history_markdown(guardian: Guardian):
        """Generates a Markdown string listing a guardian's children's enrolments."""

        # NOTE: This is markdown, so the line changes and white spaces are important!
        template = Template(CHILDREN_EVENT_HISTORY_MARKDOWN_TEMPLATE)
        context = Context({"guardian": guardian})
        return template.render(context).strip()
